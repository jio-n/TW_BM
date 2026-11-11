"""Boundary tests for truthful progress reporting; no research or network calls."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

KIT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(KIT/'scripts'))
import review as r


class ReviewTests(unittest.TestCase):
    def setUp(self):
        self.cfg=json.loads((KIT/'templates/project.json').read_text(encoding='utf-8'))
        self.cfg['scope']['include']=['Synthetic eligible class']
        self.cfg['scope']['exclude']=['Synthetic excluded class']
        self.data={t:[] for t in r.TABLES}
        self.add('queries',query_id='Q1',source='SyntheticDB',query_text='synthetic',planned_limit=10)
        self.add('papers',paper_id='P1',title='Synthetic example',url='https://example.org/p1')

    def add(self,table,**row):
        item=r.normalize(table,row);self.data[table].append(item);return item

    def run_row(self,rid='R1',ssid='S1',total=10,kind='exact',rank=1,pid='P1',**kw):
        row=self.add('runs',run_id=rid,query_id='Q1',search_set_id=ssid,executed_at='2026-11-11T00:00:00+00:00',semantics='checked',total_hits=total,total_kind=kind,returned_count=1,**kw)
        self.add('hits',hit_id='H'+rid,run_id=rid,rank=rank,paper_id=pid)
        return row

    def test_failed_search_cannot_be_zero_hits(self):
        failed=self.add('runs',run_id='R1',query_id='Q1',search_set_id='S1',executed_at='2026-11-11',status='failed',total_hits=0,total_kind='exact',returned_count=0)
        self.assertTrue(r.audit(self.cfg,self.data)['errors'])
        failed.update(total_hits='',total_kind='unknown',returned_count='')
        self.assertFalse(r.audit(self.cfg,self.data)['errors'])
        self.assertEqual(r.summarize(self.cfg,self.data)['counts']['required_queries_unsearched'],1)

    def test_success_zero_is_distinct_from_failure(self):
        self.add('runs',run_id='R1',query_id='Q1',search_set_id='S1',executed_at='2026-11-11',semantics='checked',total_hits=0,total_kind='exact',returned_count=0)
        s=r.summarize(self.cfg,self.data)['search_sets'][0]
        self.assertEqual(s['remaining_slots'],0)
        self.assertTrue(s['scope_closed'])

    def test_rank_holes_are_not_hidden_by_max_rank(self):
        self.run_row(rank=1);self.run_row('R2',rank=3)
        s=r.summarize(self.cfg,self.data)['search_sets'][0]
        self.assertEqual((s['first_missing_rank'],s['retrieved_slots'],s['remaining_to_target']),(2,2,8))

    def test_repeated_page_does_not_inflate_coverage(self):
        self.run_row();self.run_row('R2')
        self.assertEqual(r.summarize(self.cfg,self.data)['search_sets'][0]['retrieved_slots'],1)

    def test_snapshot_rank_changed_is_not_completed(self):
        self.add('papers',paper_id='P2',title='Other synthetic',url='https://example.org/p2')
        self.run_row(total=1);self.run_row('R2',total=1,pid='P2')
        s=r.summarize(self.cfg,self.data)['search_sets'][0]
        self.assertFalse(s['scope_closed']);self.assertIsNone(s['remaining_slots'])
        self.assertTrue(r.audit(self.cfg,self.data)['warnings'])

    def test_separate_snapshots_and_approximate_totals(self):
        self.run_row();self.run_row('R2','S2',kind='approximate',rank=2)
        rows=r.summarize(self.cfg,self.data)['search_sets']
        self.assertEqual(len(rows),2);self.assertEqual(rows[1]['first_missing_rank'],1)
        self.assertIsNone(rows[1]['remaining_slots'])

    def test_uncertain_search_cannot_close_scope(self):
        row=self.run_row(total=1);row['semantics']='uncertain'
        self.assertFalse(r.summarize(self.cfg,self.data)['search_sets'][0]['scope_closed'])

    def test_saved_file_does_not_mean_read(self):
        self.data['papers'][0].update(download_status='saved',local_path='synthetic.pdf')
        counts=r.summarize(self.cfg,self.data)['counts']
        self.assertEqual(counts['saved_unread'],1);self.assertEqual(counts['read_sections_or_full'],0)

    def test_complete_extraction_requires_located_evidence(self):
        p=self.data['papers'][0];p.update(extraction_status='complete',reading_status='sections')
        self.assertTrue(r.audit(self.cfg,self.data)['errors'])
        for i,field in enumerate(self.cfg['required_extraction_fields']):
            self.add('evidence',evidence_id='E'+str(i),paper_id='P1',field=field,value='synthetic evidence',url=p['url'],locator='Table 1',verification='confirmed')
        self.assertFalse(r.audit(self.cfg,self.data)['errors'])

    def test_orphan_hit_and_rank_empty_are_errors(self):
        self.add('hits',hit_id='H1',run_id='missing',paper_id='P1',rank='')
        self.assertTrue(r.audit(self.cfg,self.data)['errors'])

    def test_missing_citations_remain_unassessed(self):
        p=self.data['papers'][0];p.update(relevance='3',relevance_reason='synthetic relevance',year='2026')
        result=r.priority(p,self.cfg)
        self.assertEqual(result['score'],90);self.assertEqual(result['score_known_weight'],.9)
        self.assertEqual(result['score_upper'],100)
        p.update(citation_count='0',citation_source='SyntheticDB',citation_checked_at='2026-11-11')
        self.assertEqual(r.priority(p,self.cfg)['score_known_weight'],1)

    def test_change_weights_changes_reading_priority(self):
        p=self.data['papers'][0];p.update(relevance='3',year='2018')
        other=dict(p,relevance='1',year='2026')
        self.assertGreater(r.priority(p,self.cfg)['score'],r.priority(other,self.cfg)['score'])
        self.cfg['priority']['weights']=dict(relevance=.1,recency=.8,citations=.1)
        self.assertLess(r.priority(p,self.cfg)['score'],r.priority(other,self.cfg)['score'])

    def test_small_sample_yield_is_not_promised(self):
        self.run_row();self.data['papers'][0].update(screening='include',screening_reason='Synthetic eligible')
        s=r.summarize(self.cfg,self.data)['search_sets'][0]
        self.assertEqual(s['yield_pct'],100);self.assertIn('不明',s['prospect'])

    def test_done_task_requires_read_state_and_valid_target(self):
        task=self.add('tasks',task_id='T1',action='read_fulltext',target_type='paper',target_id='P1',status='done',completed_at='2026-11-11',evidence_ref='https://example.org/p1')
        self.assertTrue(r.audit(self.cfg,self.data)['errors'])
        task.update(target_type='query',target_id='Q1',action='search_more')
        self.assertFalse(r.audit(self.cfg,self.data)['errors'])

    def test_predeclared_recovery_cannot_be_posthoc(self):
        self.run_row()
        self.add('known_items',test_id='K1',paper_id='P1',query_id='Q1',database_indexed='yes',registered_at='2026-11-12',found_run_id='R1',test_type='predeclared')
        self.assertTrue(r.audit(self.cfg,self.data)['errors'])

    def test_exploration_includes_papers_with_no_scores(self):
        for i in range(2,40):self.add('papers',paper_id=f'P{i}',title='Synthetic'+str(i),url=f'https://example.org/p{i}')
        actions=r.next_actions(self.cfg,self.data,r.summarize(self.cfg,self.data))
        self.assertEqual(sum(a['lane']=='探索枠' for a in actions),5)
        self.assertEqual(len([a for a in actions if a['action']=='screen']),25)

    def test_required_empty_plan_cannot_pass_all_gates(self):
        self.data['queries']=[]
        self.assertFalse(all(g['passed'] for g in r.summarize(self.cfg,self.data)['plan_checks']))

    def test_user_request_first(self):
        self.add('tasks',task_id='REQ1',action='search_more',target_type='query',target_id='Q1',reason='User instruction',created_at='2026-11-11')
        actions=r.next_actions(self.cfg,self.data,r.summarize(self.cfg,self.data))
        self.assertEqual(actions[0]['action_id'],'REQ1')

    def test_cli_init_requests_idempotency_and_history(self):
        with tempfile.TemporaryDirectory(dir=KIT/'tests') as folder:
            project=Path(folder)/'synthetic-review'
            def cli(*args):
                result=subprocess.run([sys.executable,str(KIT/'scripts/review.py'),*args,'--project',str(project)],capture_output=True,encoding='utf-8')
                self.assertEqual(result.returncode,0,result.stderr+result.stdout)
            cli('init','--title','Synthetic soil review','--topic','Soil mechanisms','--as-of','2026-11-11')
            cfg,data=r.load(project);self.assertFalse(data['papers']);self.assertEqual(cfg['topic'],'Soil mechanisms')
            packet=Path(folder)/'synthetic.json';packet.write_text(json.dumps({'queries':self.data['queries'],'papers':self.data['papers']}),encoding='utf-8')
            cli('ingest','--file',str(packet))
            packet.write_text(json.dumps({'requests':[dict(request_id='TEST1',action='read_fulltext',target_type='paper',target_id='P1',priority=1,reason='Synthetic user instruction')]}),encoding='utf-8')
            cli('import-requests','--file',str(packet));n=len(r.events(project))
            cli('import-requests','--file',str(packet));self.assertEqual(len(r.events(project)),n)
            cfg,data=r.load(project);self.assertEqual(len(data['tasks']),1);self.assertEqual(data['papers'][0]['reading_status'],'not_started')
            packet.write_text(json.dumps({'requests':[dict(action='extract',target_type='paper',target_id='P1',priority=1,reason='Synthetic without supplied request ID')]}),encoding='utf-8')
            cli('import-requests','--file',str(packet));cli('import-requests','--file',str(packet))
            cfg,data=r.load(project);self.assertEqual(len(data['tasks']),2)
            self.assertEqual(r.audit(cfg,data,project)['status'],'WARN')  # Scope deliberately unset.
            cfg['topic']='manual change';r.dump(project/'project.json',cfg)
            self.assertTrue(any('直接編集' in w for w in r.audit(cfg,data,project)['warnings']))


if __name__=='__main__':unittest.main()

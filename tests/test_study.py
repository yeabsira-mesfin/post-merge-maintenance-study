import unittest
from research.study import origin,review_metrics,classify_event,analyze,interval

class StudyTests(unittest.TestCase):
    def test_bot_username_alone_is_not_provenance(self):
        self.assertEqual(origin({'login':'ai-bot','type':'User'})['origin'],'unknown')
        self.assertEqual(origin({'login':'alice','type':'User'})['origin'],'unknown')
        row=origin({'login':'dependabot[bot]','type':'Bot','id':49699333})
        self.assertEqual(row['automation_kind'],'dependency-update bot')
        self.assertNotIn('agentic',row['origin'])
    def test_review_cutoff_and_author_exclusion(self):
        rows=[{'user':{'id':1},'submitted_at':'2026-01-02T00:00:00Z','state':'APPROVED'},{'user':{'id':2},'submitted_at':'2026-01-04T00:00:00Z','state':'APPROVED'},{'user':{'id':3},'submitted_at':'2026-01-02T00:00:00Z','state':'COMMENTED'}]
        metrics=review_metrics(rows,'2026-01-01T00:00:00Z','2026-01-03T00:00:00Z',1)
        self.assertEqual(metrics['distinct_reviewers'],1);self.assertFalse(metrics['approval_present']);self.assertEqual(metrics['hours_to_merge'],48)
    def test_latest_review_state_is_used(self):
        rows=[{'user':{'id':1},'submitted_at':f'2026-01-0{day}T00:00:00Z','state':state} for day,state in [(2,'APPROVED'),(3,'CHANGES_REQUESTED')]]
        m=review_metrics(rows,'2026-01-01T00:00:00Z','2026-01-04T00:00:00Z')
        self.assertFalse(m['approval_present']);self.assertEqual(m['changes_requested_count'],1)
    def test_file_edit_never_becomes_confirmed_defect(self):
        self.assertEqual(classify_event('Fix parser edge case','abc',12),'fix-keyword edit')
        self.assertEqual(classify_event('update docs','abc',12),'later file edit')
        self.assertEqual(classify_event('Revert #123','abc',12),'later file edit')
        self.assertEqual(classify_event('Revert #12','abc',12),'explicit revert reference')
    def test_censored_and_incomplete_excluded(self):
        base={'repository':'o/r','additions':1,'deletions':1,'reviews_complete':True,'tracking_complete':True,'right_censored':False,'approval_present':True,'events':[{}]}
        data=analyze([base,{**base,'right_censored':True},{**base,'tracking_complete':False},{**base,'reviews_complete':False}])
        self.assertEqual(data['by_approval'][0]['eligible_prs'],1)
        self.assertEqual(data['by_approval'][0]['edit_rate'],1)
        self.assertIsNone(data['by_approval'][1]['edit_rate'])
    def test_wilson_uncertainty_and_empty_denominator(self):
        self.assertEqual(interval(1,2),[0.0945,0.9055]);self.assertIsNone(interval(0,0))
    def test_unknown_origin_does_not_preclude_review_analysis(self):
        self.assertEqual(origin({})['origin'],'unknown')
        self.assertEqual(review_metrics([],'2026-01-01T00:00:00Z','2026-01-02T00:00:00Z')['merge_without_formal_review'],True)

if __name__=='__main__': unittest.main()

"""A small descriptive post-merge study. File edits are not defect attribution."""
import argparse,json,re,math
from datetime import datetime,timezone,timedelta
from pathlib import Path
from urllib.parse import quote,urlencode
from .common import JsonClient,CollectionError,instant,write_outputs
ROOT=Path(__file__).resolve().parents[1]


def origin(user):
    if user.get('type')=='Bot':
        routine=user.get('login') in {'dependabot[bot]','renovate[bot]'}
        return {'origin':'verified automation','automation_kind':'dependency-update bot' if routine else 'unclassified bot','evidence':'GitHub user.type=Bot; not proof of coding-agent authorship','account_id':user.get('id')}
    return {'origin':'unknown','automation_kind':None,'evidence':'A User account does not establish whether code was human- or AI-authored.','account_id':None}


def review_metrics(reviews,created,merged,author_id=None):
    pre=[r for r in reviews if r.get('submitted_at') and instant(r['submitted_at'])<=instant(merged) and r.get('state')!='PENDING' and r.get('user',{}).get('id')!=author_id]
    latest={}
    for r in sorted(pre,key=lambda r:r['submitted_at']):
        identity=r.get('user',{}).get('id')
        if identity is not None: latest[identity]=r.get('state')
    return {'distinct_reviewers':len(latest),'review_count':len(pre),'approval_present':any(s=='APPROVED' for s in latest.values()),'changes_requested_count':sum(r.get('state')=='CHANGES_REQUESTED' for r in pre),'merge_without_formal_review':not pre,'hours_to_merge':round((instant(merged)-instant(created)).total_seconds()/3600,2)}


def classify_event(message,merge_sha,pr_number):
    if re.search(r'\brevert',message,re.I) and (merge_sha in message or re.search(rf'(?<!\d)#{pr_number}(?!\d)',message)):
        return 'explicit revert reference'
    if re.search(r'\b(security|CVE-\d|vulnerab)',message,re.I): return 'security-keyword edit'
    if re.search(r'\b(fix(?:es|ed)?|bug|regression)\b',message,re.I): return 'fix-keyword edit'
    if re.search(r'\brefactor',message,re.I): return 'refactor-keyword edit'
    return 'later file edit'


def interval(successes,n):
    if not n: return None
    z=1.96; p=successes/n;den=1+z*z/n
    center=(p+z*z/(2*n))/den;half=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/den
    return [round(max(0,center-half),4),round(min(1,center+half),4)]


def analyze(rows):
    # Censored/incomplete cases are not silently treated as zero maintenance.
    groups=[]
    for approval in (True,False):
        subset=[r for r in rows if r['reviews_complete'] and r['tracking_complete'] and not r['right_censored'] and r['approval_present']==approval]
        touched=sum(bool(r['events']) for r in subset)
        groups.append({'group':'approval recorded' if approval else 'no approval recorded','eligible_prs':len(subset),'prs_with_later_edits':touched,'edit_rate':touched/len(subset) if subset else None,'wilson_95_interval':interval(touched,len(subset))})
    strata=[]
    for repo in sorted({r['repository'] for r in rows}):
        for size in ('small','large'):
            subset=[r for r in rows if r['repository']==repo and ('small' if r['additions']+r['deletions']<=100 else 'large')==size and r['reviews_complete'] and r['tracking_complete'] and not r['right_censored']]
            if subset: strata.append({'repository':repo,'size_stratum':size,'prs':len(subset),'prs_with_later_edits':sum(bool(r['events']) for r in subset)})
    return {'by_approval':groups,'by_repository_and_size':strata,'interpretation':'Descriptive file-level associations only. No causal estimate, AI-vs-human comparison, or defect rate.'}


def select_prs(client,repo,config):
    query=f'repo:{repo} is:pr is:merged merged:<{config["merged_before"]}'
    data=client.get('https://api.github.com/search/issues?'+urlencode({'q':query,'sort':'created','order':'desc','per_page':config['prs_per_repository'],'page':1}))
    if data.get('incomplete_results'): raise CollectionError('GitHub search is incomplete')
    return [item['number'] for item in data.get('items',[])]


def collect(config,client):
    now=datetime.now(timezone.utc);rows=[];errors=[];selection={}
    for repo in config['repositories']:
        if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+',repo): raise ValueError('Invalid repository')
        try:
            metadata=client.get('https://api.github.com/repos/'+repo)
            head=config.get('pinned_heads',{}).get(repo) or client.get(f'https://api.github.com/repos/{repo}/commits/{quote(metadata["default_branch"],safe="")}')['sha']
            numbers=config.get('pinned_prs',{}).get(repo) or select_prs(client,repo,config)
            selection[repo]={'pr_numbers':numbers,'default_branch':metadata['default_branch'],'head_sha':head,'language':metadata.get('language')}
        except (CollectionError,KeyError) as e:
            errors.append({'repository':repo,'error':str(e)});continue
        for number in numbers:
            try:
                prefix=f'https://api.github.com/repos/{repo}/pulls/{number}'
                pr=client.get(prefix)
                if not pr.get('merged_at') or pr.get('base',{}).get('ref')!=metadata['default_branch']:
                    errors.append({'repository':repo,'pr':number,'error':'Not merged to the observed default branch'});continue
                merged=instant(pr['merged_at']);end=min(merged+timedelta(days=config['window_days']),now)
                files,files_complete=client.pages(prefix+'/files',max_pages=3)
                reviews,reviews_complete=client.pages(prefix+'/reviews',max_pages=2)
                paths=sorted(f['filename'] for f in files if f.get('status')!='removed')
                tracked=paths[:config['max_files_per_pr']]
                events={};history_complete=True
                for path in tracked:
                    url=f'https://api.github.com/repos/{repo}/commits?'+urlencode({'sha':head,'path':path,'since':merged.isoformat(),'until':end.isoformat()})
                    history,complete=client.pages(url,max_pages=1)
                    history_complete=history_complete and complete
                    for commit in history:
                        date=commit['commit']['committer']['date']
                        if commit['sha']==pr['merge_commit_sha'] or not merged<instant(date)<=end:continue
                        msg=commit['commit']['message']
                        event=events.setdefault(commit['sha'],{'sha':commit['sha'],'date':date,'url':commit['html_url'],'message':msg.splitlines()[0][:240],'classification':classify_event(msg,pr['merge_commit_sha'],number),'files':[],'attribution':'file overlap only; introduced-line attribution not established','days_after_merge':round((instant(date)-merged).total_seconds()/86400,3)})
                        event['files'].append(path)
                metrics=review_metrics(reviews,pr['created_at'],pr['merged_at'],pr.get('user',{}).get('id'))
                row={'repository':repo,'number':number,'url':pr['html_url'],'title':pr['title'],'created_at':pr['created_at'],'merged_at':pr['merged_at'],'merge_commit_sha':pr['merge_commit_sha'],'head_sha':head,'language':metadata.get('language'),'additions':pr.get('additions',0),'deletions':pr.get('deletions',0),'changed_files':pr.get('changed_files',len(files)),**metrics,**origin(pr.get('user',{})),'review_comments':pr.get('review_comments'),'review_comments_scope':'all-time count, not pre-merge review rigor','reviews_complete':reviews_complete,'files_complete':files_complete,'tracked_files':tracked,'untracked_files':max(0,len(paths)-len(tracked)),'tracking_complete':files_complete and history_complete and len(paths)==len(tracked) and len(files)==pr.get('changed_files',len(files)) and not any(f.get('status') in ('removed','renamed') for f in files),'history_pages_complete':history_complete,'right_censored':now<merged+timedelta(days=config['window_days']),'window_days':config['window_days'],'observed_days':round((end-merged).total_seconds()/86400,2),'events':sorted(events.values(),key=lambda e:e['date']),'source':prefix}
                rows.append(row)
            except (CollectionError,KeyError,ValueError) as e: errors.append({'repository':repo,'pr':number,'error':str(e)})
    return {'schema_version':1,'project':'Post-Merge Maintenance Study','data_kind':'public GitHub observations','generated_at':now.isoformat(),'selection':selection,'config':config,'pull_requests':rows,'analysis':analyze(rows),'errors':errors,'sources':client.sources,'request_count':client.requests,'limitations':['Small purposive Python sample; no population inference.','File overlaps and message keywords are maintenance candidates, not defects.','Missing or renamed/deleted paths and page/file caps make tracking incomplete.','User accounts remain unknown origin; no AI-versus-human finding.','Review activity is a proxy, not a direct measure of quality.']}


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--config',type=Path,default=ROOT/'sample-config.json');p.add_argument('--output',type=Path,default=ROOT/'public/data/study.json');p.add_argument('--cache',default=str(ROOT/'.cache'));p.add_argument('--refresh',action='store_true');p.add_argument('--offline',action='store_true');args=p.parse_args()
    config=json.loads(args.config.read_text())
    if not 1<=config['window_days']<=90 or not 1<=config['prs_per_repository']<=5 or len(config['repositories'])>3 or not 1<=config['max_files_per_pr']<=10: p.error('Sample bounds exceeded')
    data=collect(config,JsonClient(args.cache,args.refresh,max_requests=70,offline=args.offline))
    rows=[{k:r[k] for k in ('repository','number','origin','additions','deletions','distinct_reviewers','approval_present','hours_to_merge','reviews_complete','tracking_complete','right_censored')}|{'later_edit_commits':len(r['events'])} for r in data['pull_requests']]
    write_outputs(args.output,rows,data,'pr_observations')
    print(json.dumps({'prs':len(rows),'analysis':data['analysis'],'errors':data['errors'],'output':str(args.output)},indent=2))
    if not rows: raise SystemExit(1)

if __name__=='__main__':main()

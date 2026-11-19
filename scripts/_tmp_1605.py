import re, os, shutil, subprocess
W='/home/openclaw/.openclaw/workspace'
os.chdir(W)

# 1) checklist：零交付檢查要豁免 heartbeat kind（delivery=null 係設計如此，唔係零交付）
p='docs/heartbeat-checklist.md'
s=open(p).read()
anchor='- **新模式：`receipt status=ok` 但 `delivery_attempt_state=not-started` → 零交付**'
i=s.find(anchor)
assert i>=0, 'zero-delivery rule not found'
excl='- ⚠️ **豁免**：`9dc7d6c3` heartbeat-main 係 `kind=heartbeat`、`delivery=null` → receipt 一定係 `not-started`（心跳唔會派送 Telegram，唔算零交付）。零交付檢查只適用於 **agentTurn 簡報／job**。\n'
if '⚠️ **豁免**：`9dc7d6c3` heartbeat-main' not in s:
    s = s[:i] + excl + s[i:]
    open(p,'w').write(s)
    print('checklist exemption added')
else:
    print('checklist exemption already present')

# 2) MEMORY.md 追加
mem=open('/tmp/_mem_1605.txt').read()
with open('MEMORY.md','a') as f: f.write(mem)
for dst in ['/home/openclaw/Second-brain/MEMORY.md','/home/openclaw/Max-backup/MEMORY.md']:
    open(dst,'w').write(open('MEMORY.md').read())
print('MEMORY.md lines =', sum(1 for _ in open('MEMORY.md')))

# 3) skill 版本 +0.0.1 + 更新記錄
sk='.openclaw/skills/novel-site-standards/SKILL.md'
t=open(sk).read()
m=re.search(r'version: ([0-9.]+)', t)
old=m.group(1); parts=old.split('.')
ver='.'.join(parts[:2]+[str(int(parts[2])+1)])
t=t.replace('version: '+old, 'version: '+ver, 1)
note=open('/tmp/_skill_1605.txt').read()
t=t.rstrip('\n')+'\n'+note
open(sk,'w').write(t)
print('skill', old, '->', ver, '| bytes', os.path.getsize(sk))

# 4) 三倉 commit + push
def run(c, cwd=None):
    return subprocess.run(c, shell=True, cwd=cwd, capture_output=True, text=True)
r=run('git add scripts/moontv_keepalive.py && git commit -m \'chore(moontv): wrong_upstream 提示只喺真正通知時先入 issues\' && git pull --rebase origin main && git push', W)
print('ws commit:', r.stdout.strip().splitlines()[-3:] if r.stdout else r.stderr[:200])
for repo, msg in [('/home/openclaw/Second-brain','docs: MEMORY.md + skill v2.9.196'),('/home/openclaw/Max-backup','docs: MEMORY.md + skill v2.9.196')]:
    r=run('git add -A . && git commit -m \''+msg+'\' && git pull --rebase origin main && git push', repo)
    print(repo.split('/')[-1]+':', r.stdout.strip().splitlines()[-2:] if r.stdout else r.stderr[:200])
r=run('git add -A . && git commit -m \'docs: checklist 零交付檢查豁免 heartbeat + skill v2.9.196 + MEMORY\' && git pull --rebase origin main && git push', W)
print('ws commit2:', r.stdout.strip().splitlines()[-3:] if r.stdout else r.stderr[:200])

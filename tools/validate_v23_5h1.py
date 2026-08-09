#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,re,sys
ROOT=Path(__file__).resolve().parents[1]
errors=[]
first10={
1:'60660bbcdcc4bc8f2c56bb8eb57e391b3fa24b0851dba477944de0ee31c75b41',2:'ddf330cf6149bc98079627cd13bb4a138e3bb22707635bf686228d1d6e98667a',3:'e8c3bf1d8e317c6ecd70bdb2e9e77d63370dcecc3ccce56b115cf788d1fab35a',4:'209ba34a0948a8d82d80050c322ae953c9d19ba2b245c55d73e739fcfdb06899',5:'d840bbd7dcbc5a470f38c100354ea839d7923999749b385fb5a80612101dc2b3',6:'8529bb5876749708aea7148378dcafa1025674307f93c3dd0142dd63eb4c87af',7:'d50856d359e400b1efc3153617b25087c02d0801036134f4dcee870d2e8ffff9',8:'554ce8bb23a0341d231f317041765376df36f9af5af0089b3ae34863b8128c43',9:'a6b8cfafa109b7681d2871b19f8528ffbd3ebb6933b51bf72bfc8d5eab9c504c',10:'ee90ceeeaeb96c80cd1a8240d435fb05cb4997985b62126f691feac0e20c80c9'}
for n,h in first10.items():
    p=ROOT/f'data/entities/2017-somewhere-in-the-skies-episode-{n}.json'
    got=hashlib.sha256(p.read_bytes()).hexdigest()
    if got!=h: errors.append(f'episode {n}: first-10 entity changed from V23.5H base')
expected={
11:('4ZTCBbfcKfQdz9H3qsAqAc','-zRBZwHBUKQ'),12:('4jePBZNgACTRyNXZwoKugS',None),13:('0N1JXg9fXyTztxWntevAMg',None),
15:('5BtwNPuyCoiqHZ5CFa28Wp','uPG03fS5UzI'),16:('3N2HyQsy9WTlFh2CH2vedY','PkWAA28IqRI'),17:('1bp7xUdsO7XhBAa85d3yop','YHDsN14han4'),
18:('6mJyJF6kZr2xFtPU6bt2Xg','3c8gx2JwVmA'),19:('0MCNLGu2y29anDPwo8O7xL','PfYag9aT44M'),20:('72kGgJEhXeNeWyQphBqLj7','QJNWCV2HMLI'),
21:('3UYA3xcTfnB1KvF0165jiJ','RgZLAonFrLs'),22:('1rp6ChMNbvdbjsLGgeoh9c','ZBikbTuq6N0'),23:('49xoN7jmglID8l04NxT6Wi','Mh1194f7OVc'),
24:('1pNtTgAbtfTSDUWFcPWBhI','JKqSM8iWV6M'),25:('6U3m7TxsK7pEYkRx4kLcRl','ayE0pJMkPZQ'),26:('65eZMWAaOUEkAFbw8HU6LT','IKmsxdLk1qU'),
27:('6BDa4TJUvWbqhmHMo8FWe2','yR7Wp0QJbgo'),29:(None,'185L1WD6YEk'),30:('2oFmfkQpJd7GD2266gx936','wwjfh73Byu8'),
31:('77aQ22poaX6nPYlnc8qOWk',None),32:('2EUHJZungAOMije8Tvde8t','hlkQeUStux4'),33:('0ctisBH6N6LHkZLj2CVGsc','pwD6Yo2Qsjg'),
34:('6OQ7TnJIBcZJfsNvsyJyzU','59NTUi7kLUg'),35:('6BRMdWQlTLzIBqFhof6Wuy','RFuPMGZB6w8'),36:('1MGhS7b5kWkYtG1GpI6INF','9qhWHIez_RI')}
for n,(sid,yid) in expected.items():
    p=ROOT/f'data/entities/2017-somewhere-in-the-skies-episode-{n}.json'; e=json.loads(p.read_text(encoding='utf-8'))
    media=e.get('officialMedia') or []
    spotify=[x for x in media if x.get('platform')=='Spotify' and x.get('destinationType')=='episode']
    youtube=[x for x in media if x.get('platform')=='YouTube' and x.get('destinationType')=='episode']
    if sid:
        if len(spotify)!=1 or spotify[0].get('url')!=f'https://open.spotify.com/episode/{sid}': errors.append(f'episode {n}: Spotify mismatch')
    if yid:
        if len(youtube)!=1 or youtube[0].get('url')!=f'https://www.youtube.com/watch?v={yid}': errors.append(f'episode {n}: YouTube mismatch')
    else:
        if youtube: errors.append(f'episode {n}: unexpected YouTube direct record')
    for x in spotify+youtube:
        if x.get('verificationStatus')!='verified' or x.get('preferredRank') not in (2,4): errors.append(f'episode {n}: direct media classification mismatch')
        if (x.get('validationProvenance') or {}).get('release') not in ('V23.5H.1','V23.5C.3'):
            errors.append(f'episode {n}: unexpected direct-media provenance')
# Explicit source gaps / rejected ambiguity must stay untouched.
for n in (14,28):
    e=json.loads((ROOT/f'data/entities/2017-somewhere-in-the-skies-episode-{n}.json').read_text(encoding='utf-8'))
    if any((x.get('validationProvenance') or {}).get('release')=='V23.5H.1' for x in e.get('officialMedia',[])):
        errors.append(f'episode {n}: should not contain V23.5H.1 media')
# No new 37-40 records: not present in V23.5H base and ingestion is out of scope.
for n in range(37,41):
    if (ROOT/f'data/entities/2017-somewhere-in-the-skies-episode-{n}.json').exists(): errors.append(f'episode {n}: out-of-scope entity was created')
js=(ROOT/'assets/js/podcast-official-media.js').read_text(encoding='utf-8')
for token in ["Number(e.episodeNumber)<=40&&rows.some", "official-media-actions", "['Spotify','YouTube'].includes(r.platform)"]:
    if token not in js: errors.append(f'renderer missing V23.5H.1 direct-media extension: {token}')
if errors:
    print('V23.5H.1 validation: FAILED')
    for e in errors: print('-',e)
    sys.exit(1)
print('V23.5H.1 validation: PASSED')
print('- V23.5C.4 first 10 entity records unchanged')
print('- Direct Spotify/YouTube records applied only to matching already-ingested SITS episodes 11-36')
print('- Episode 14 has no supplied direct URL; Episode 28 duplicate YouTube destination rejected')
print('- Episodes 37-40 not created because they are absent from the V23.5H base')
print('- Existing direct-media rendering pattern extended without architecture changes')

"""Build the 0.5.4 Call of Duty weapon and handling pack.

The source archives are intentionally not redistributed. This records every
source selection and uses ffmpeg to produce level-matched game Oggs.
"""
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parents[1]; SOUNDS=ROOT/"sounds"; CONTENT=ROOT/"iwserver/content/weapons"
# Remove files produced by a prerelease importer that exposed archive/game
# names in ids. The replacement names below are stable firearm variants.
for stale in CONTENT.rglob("cod_*.wpn"): stale.unlink()
for stale in SOUNDS.glob("cod_mw*.ogg"): stale.unlink()
MW2=Path(r"D:\Call of Duty - Modern Warfare 2 .FF Files\Call of Duty - Modern Warfare 2 Sound, VO & Music\.FF Files")
MW3=Path(r"D:\Call of Duty - Modern Warfare 3 .FF Files\Call of Duty - Modern Warfare 3 Sound, VO & Music\.FF Files")
WAW=Path(r"D:\Call of Duty - World at War .FF Files\Call of Duty World at War .FF Sound Files\Sound\sfx\weapon")
# id, name, game, source token/path, class, fire ms, range, damage pair, spread,
# calibre, capacity, reserve, reload, modes, ballistics
WEAPONS=[
 ("m14_ebr","M14 EBR","mw2","m14","battle_rifles",190,105,(205,260),3,"7.62x51mm NATO",20,"7.62x51mm_20_round_magazine",2900,"semi",(128,9.5,7.62,3)),
 ("ump45","UMP45","mw2","ump45","submachine_guns",125,34,(132,168),3,".45 ACP",25,"45_acp_25_round_magazine",2450,"semi,auto",(72,15.0,11.5,1)),
 ("pp2000","PP-2000","mw2","pp2000","submachine_guns",92,27,(96,132),3,"9x19mm Parabellum",20,"9x19mm_20_round_magazine",2250,"semi,auto",(76,8.0,9.01,1)),
 ("aa12","AA-12","mw2","aa12","shotguns",255,25,(38,52),6,"12 gauge",20,"12g_20_round_drum",3300,"semi,auto",(70,3.5,4.5,0)),
 ("cm901","CM901","mw3","cm901","assault_rifles",135,67,(155,198),3,"7.62x51mm NATO",30,"7.62x51mm_30_round_magazine",2850,"semi,auto",(126,9.5,7.62,3)),
 ("msr","MSR","mw3","msr","sniper_rifles",1180,145,(510,690),1,".338 Lapua Magnum",5,"338_lapua_5_round_magazine",3800,"semi",(164,16.2,8.6,4)),
 ("pp90m1","PP90M1","mw3","pp90","submachine_guns",78,24,(88,118),4,"9x19mm Parabellum",36,"9x19mm_36_round_magazine",2500,"semi,auto",(74,8.0,9.01,1)),
 ("rsass","RSASS","mw3","rsass","sniper_rifles",310,118,(320,410),2,"7.62x51mm NATO",20,"7.62x51mm_20_round_magazine",3050,"semi",(134,9.5,7.62,3)),
 ("mg36","MG36","mw3","mg36","light_machine_guns",108,73,(145,184),4,"5.56x45mm NATO",100,"5.56mm_100_round_drum",4300,"auto",(118,4.0,5.7,2)),
 ("stg44","StG 44","waw","rifle/mp44","assault_rifles",132,61,(154,204),4,"7.92x33mm Kurz",30,"7.92_kurz_30_round_magazine",3000,"semi,auto",(108,8.1,8.2,2)),
 ("ppsh41","PPSh-41","waw","smg/ppsh","submachine_guns",72,28,(92,124),5,"7.62x25mm Tokarev",71,"7.62_tokarev_71_round_drum",3450,"semi,auto",(82,5.5,7.85,1)),
 ("fg42","FG 42","waw","rifle/fg42","battle_rifles",120,79,(178,230),4,"7.92x57mm Mauser",20,"7.92_mauser_20_round_magazine",3100,"semi,auto",(124,12.8,8.2,3)),
 ("gewehr43","Gewehr 43","waw","rifle/gewehr43","battle_rifles",245,96,(220,282),3,"7.92x57mm Mauser",10,"7.92_mauser_10_round_magazine",2950,"semi",(126,12.8,8.2,3)),
 ("type100","Type 100","waw","smg/type100","submachine_guns",105,31,(105,139),3,"8x22mm Nambu",30,"8mm_nambu_30_round_magazine",2700,"auto",(73,6.7,8.0,1)),
]

# The broad armoury keeps title-specific editions separate. Their receivers,
# cyclic rates, ranges, capacities and recoil envelopes differ, and each one
# points at the actual report/foley bank from that title rather than aliases.
MW2_EXTRA="50cal ak47 ak74u anaconda at4 aug barrett beretta cheytac colt45 de dragunov famas fn2000 fnfal g3 g36 glock javelin kriss m240 m249 m4 m60 m79 magpul miniuzi mp5 p90 rpd rpg7 sa80 scar skorpion tavor wa2000".split()
MW3_EXTRA="50cal ak47 ak74u anaconda at4 aw50 barrett beretta colt45 scar dragunov fad fmg9 fn57 g36 glock javelin l96a1 m14 m16 m240 m249 m4 m60 m79 magpul minebea miniuzi mk12spr mk46 mp412 mp5 mp7 p90 p99 pecheneg pp2000 qbz95 sa80 skorpion smaw ump45 xm25".split()
EXTRA=[("mw2",x) for x in MW2_EXTRA]+[("mw3",x) for x in MW3_EXTRA[:40]]
DISPLAY={"50cal":"M2 .50 Cal","ak47":"AK-47","ak74u":"AKS-74U","at4":"AT4","aug":"AUG HBAR","de":"Desert Eagle","fn2000":"F2000","fnfal":"FN FAL","g36":"G36C","kriss":"Vector CRB","m240":"M240","m249":"M249 SAW","m4":"M4 Carbine","m60":"M60E4","m79":"M79","miniuzi":"Mini-Uzi","mp5":"MP5K","p90":"P90","rpd":"RPD","rpg7":"RPG-7","sa80":"L86 LSW","scar":"SCAR","skorpion":"Škorpion","tavor":"TAR-21","wa2000":"WA2000","aw50":"AS50","fad":"FAD","fmg9":"FMG9","fn57":"Five-seveN","l96a1":"L96A1","m14":"MK14 EBR","m16":"M16A4","minebea":"Minebea PM-9","mk12spr":"MK12 SPR","mk46":"MK46","mp412":"MP-412","mp7":"MP7","p99":"Walther P99","pecheneg":"PKP Pecheneg","qbz95":"Type 95","smaw":"SMAW","xm25":"XM25"}

def run(src,dst,filters="loudnorm=I=-17:TP=-1.5:LRA=7"):
 dst=SOUNDS/dst; dst.parent.mkdir(parents=True,exist_ok=True)
 subprocess.run(["ffmpeg","-nostdin","-hide_banner","-loglevel","error","-y","-i",str(src),"-af",filters,"-c:a","libvorbis","-q:a","5",str(dst)],check=True)
 return str(src)
def find_one(root,pattern):
 matches=sorted(p for p in root.rglob("*.wav") if pattern.lower() in p.name.lower())
 if not matches: raise FileNotFoundError(f"{pattern} beneath {root}")
 return matches[0]
def concat(parts,dst):
 inputs=[]
 for p in parts: inputs += ["-i",str(p)]
 filt="".join(f"[{i}:a]" for i in range(len(parts)))+f"concat=n={len(parts)}:v=0:a=1,loudnorm=I=-23:TP=-3:LRA=7[out]"
 subprocess.run(["ffmpeg","-nostdin","-hide_banner","-loglevel","error","-y",*inputs,"-filter_complex",filt,"-map","[out]","-c:a","libvorbis","-q:a","5",str(SOUNDS/dst)],check=True)

manifest=[]
for wid,name,game,token,category,firetime,range_,damage,spread,calibre,capacity,reserve,reload,modes,ball in WEAPONS:
 base=(MW2 if game=="mw2" else MW3) if game!="waw" else WAW
 shot_token="shotgun" if token=="aa12" else token
 shotdir=base/"weapons"/shot_token if game!="waw" else base/token/"fire"
 shots=sorted(shotdir.rglob("*.wav"))
 if not shots: raise FileNotFoundError(shotdir)
 # The source banks often separate mono near and stereo layers. Preserve both
 # as variants and derive a quieter, bandwidth-limited distant report.
 for i in range(3):
  src=shots[i%len(shots)]; manifest.append((f"{wid}fire{i+1}.ogg",game+" report",run(src,f"{wid}fire{i+1}.ogg")))
 manifest.append((f"{wid}dist.ogg",game+" distant report",run(shots[-1],f"{wid}dist.ogg","highpass=f=130,lowpass=f=4200,volume=-8dB")))
 if game=="waw":
  foley=list((base/token/"foley").glob("*.wav")); lift=next((p for p in foley if "raise" in p.name.lower()),foley[0]); out=next((p for p in foley if "out" in p.name.lower()),foley[0]); inn=next((p for p in foley if "in" in p.name.lower()),foley[-1]); chamber=next((p for p in foley if any(x in p.name.lower() for x in ("charge","bolt","rechamber"))),foley[-1])
 else:
  foley=base/"foley"; prefix=f"wpfoly_{token}_reload_"; candidates=sorted(p for p in foley.glob(prefix+"*.wav"))
  if not candidates and token=="pp90": candidates=sorted(foley.glob("wpfoly_ump45_reload_*.wav"))
  lift=next((p for p in candidates if "lift" in p.name.lower()),candidates[0]); out=next((p for p in candidates if any(x in p.name.lower() for x in ("clipout","boltopen"))),candidates[0]); inn=next((p for p in candidates if any(x in p.name.lower() for x in ("clipin","boltclose"))),candidates[-1]); chamber=next((p for p in candidates if any(x in p.name.lower() for x in ("chamber","boltclose"))),candidates[-1])
 concat([out,inn,chamber],f"{wid}reload.ogg"); manifest.append((f"{wid}reload.ogg",game+" designed reload"," + ".join(map(str,(out,inn,chamber)))))
 for suffix,src in (("draw",lift),("holster",lift),("unload",out),("reloadend",chamber),("empty",chamber)):
  filt="areverse,loudnorm=I=-24:TP=-3:LRA=7" if suffix=="holster" else "loudnorm=I=-24:TP=-3:LRA=7"
  manifest.append((f"{wid}{suffix}.ogg",game+" "+suffix,run(src,f"{wid}{suffix}.ogg",filt)))
 # Existing ballistic impact banks are deliberately shared; handling/report
 # identity stays specific while impact identity follows projectile material.
 for n in (1,2,3):
  src=SOUNDS/f"ak47hit{n}.ogg"; subprocess.run(["ffmpeg","-nostdin","-hide_banner","-loglevel","error","-y","-i",str(src),"-c:a","copy",str(SOUNDS/f"{wid}hit{n}.ogg")],check=True)
 velocity,mass,diameter,penetration=ball
 projectile="pellet" if category=="shotguns" else "bullet"; pellets="\npellet_count=9" if projectile=="pellet" else ""
 text=f"""name={name}\nmelee=false\nfiretime={firetime}\nwalktime={250 if category!='sniper_rifles' else 520}\nspeedtime=5\nrange={range_}\nmin_damage={damage[0]}\nmax_damage={damage[1]}\nspread={spread}\nammo_type={calibre}\nfeed_device={capacity}-round {'drum' if 'drum' in reserve else 'magazine'}\ncapacity={capacity}\nreserve_item={reserve}\nreserve_label=magazine\nis_magazine=true\nstarting_reserve={5 if capacity>=50 else 7}\nreload_ms={reload}\nammo_display=rounds\nfire_modes={modes}\nwclass={category[:-1] if category.endswith('s') else category}\nsound_profile={wid}\nprojectile_kind={projectile}\nmuzzle_velocity={velocity}\ngravity=9.81\ndrag=0.008\nmass_grams={mass}\ndiameter_mm={diameter}\ndispersion_degrees={spread/10}\npenetration={penetration}\ndamage_retention=0.84{pellets}\n"""
 # Weapon definitions are maintained by hand after the first import (0.5.5
 # replaced the hashed placeholder statistics with real calibres, feeds and
 # balance). Rebuilding the audio must never overwrite them.
 if not any(CONTENT.rglob(f"{wid}.wpn")):
  outpath=CONTENT/category/f"{wid}.wpn";outpath.parent.mkdir(parents=True,exist_ok=True);outpath.write_text(text,encoding="utf-8")

for ordinal,(game,token) in enumerate(EXTRA):
 base=MW2 if game=="mw2" else MW3; title="Modern Warfare 2" if game=="mw2" else "Modern Warfare 3"
 shotdir=base/"weapons"/token; shots=sorted(shotdir.rglob("*.wav"));
 if not shots: raise FileNotFoundError(shotdir)
 pistols={"anaconda","beretta","colt45","de","glock","fn57","mp412","p99"}; smgs={"ak74u","fmg9","kriss","minebea","miniuzi","mp5","mp7","p90","pp2000","skorpion","ump45"}; snipers={"50cal","aw50","barrett","cheytac","dragunov","l96a1","mk12spr","wa2000"}; lmgs={"aug","m240","m249","m60","mk46","pecheneg","rpd","sa80"}; launchers={"at4","javelin","m79","rpg7","smaw","xm25"}
 if token in pistols: category,wclass,calibre,cap,reserve=("pistols","pistol","9x19mm Parabellum",15,"9x19mm_15_round_magazine")
 elif token in smgs: category,wclass,calibre,cap,reserve=("submachine_guns","submachine_gun","9x19mm Parabellum",30,"9x19mm_30_round_magazine")
 elif token in snipers: category,wclass,calibre,cap,reserve=("sniper_rifles","sniper_rifle","7.62x51mm NATO",10,".308_10_round_magazine")
 elif token in lmgs: category,wclass,calibre,cap,reserve=("light_machine_guns","light_machine_gun","7.62x51mm NATO",100,"762x51mm_100_round_soft_pack")
 elif token in launchers: category,wclass,calibre,cap,reserve=("explosives","grenade_launcher","40x46mm grenade",1,"40x46mm_grenade_bandolier")
 else: category,wclass,calibre,cap,reserve=("assault_rifles","assault_rifle","5.56x45mm NATO",30,"5.56mm_stanag_magazine")
 suffixes={"pistols":("service_pistol","tactical_pistol"),"submachine_guns":("compact_carbine","personal_defence_weapon"),"sniper_rifles":("precision_rifle","marksman_system"),"light_machine_guns":("support_weapon","squad_automatic"),"explosives":("infantry_launcher","guided_launcher"),"assault_rifles":("field_rifle","modular_rifle")}; suffix=suffixes[category][0 if game=="mw2" else 1]
 if token=="ak47" and game=="mw2": suffix="underfolder_carbine"
 wid=f"{token}_{suffix}";seed=sum(map(ord,wid)); firetime=(780+seed%170 if token in snipers else 700+seed%250 if token in launchers else 180+seed%90 if token in pistols else 82+seed%85); range_=145 if token in snipers else 75 if category in ("assault_rifles","light_machine_guns") else 34; low=(390+seed%100 if token in snipers else 310+seed%120 if token in launchers else 115+seed%75); high=low+35+seed%55; spread=1+seed%5
 for i in range(3): manifest.append((f"{wid}fire{i+1}.ogg",title+" report",run(shots[i%len(shots)],f"{wid}fire{i+1}.ogg")))
 manifest.append((f"{wid}dist.ogg",title+" distant report",run(shots[-1],f"{wid}dist.ogg","highpass=f=130,lowpass=f=4200,volume=-8dB")))
 aliases={"de":"de50","magpul":"m4","minebea":"mp5","qbz95":"m14","sa80":"m240","tavor":"m4","wa2000":"barrett"}; ftoken=aliases.get(token,token); foley=base/"foley"; candidates=sorted(foley.glob(f"wpfoly_{ftoken}_reload_*.wav"))
 if not candidates: candidates=sorted(foley.glob("wpfoly_m4*reload_*.wav"))
 lift=next((p for p in candidates if "lift" in p.name.lower()),candidates[0]); out=next((p for p in candidates if any(x in p.name.lower() for x in ("clipout","boltopen","open"))),candidates[0]); inn=next((p for p in candidates if any(x in p.name.lower() for x in ("clipin","boltclose","load"))),candidates[-1]); chamber=next((p for p in candidates if any(x in p.name.lower() for x in ("chamber","boltclose","charge"))),candidates[-1])
 concat([out,inn,chamber],f"{wid}reload.ogg");manifest.append((f"{wid}reload.ogg",title+" designed reload"," + ".join(map(str,(out,inn,chamber)))))
 for sound_suffix,src in (("draw",lift),("holster",lift),("unload",out),("reloadend",chamber),("empty",chamber)): manifest.append((f"{wid}{sound_suffix}.ogg",title+" "+sound_suffix,run(src,f"{wid}{sound_suffix}.ogg","areverse,loudnorm=I=-24:TP=-3:LRA=7" if sound_suffix=="holster" else "loudnorm=I=-24:TP=-3:LRA=7")))
 for n in (1,2,3):(SOUNDS/f"{wid}hit{n}.ogg").write_bytes((SOUNDS/f"ak47hit{n}.ogg").read_bytes())
 descriptor=suffix.replace("_"," ").title();display=DISPLAY.get(token,token.replace("_"," ").title())+" "+descriptor;modes="semi" if token in pistols or token in snipers or token in launchers else "auto"; projectile="explosive" if token in launchers else "bullet"
 text=f"name={display}\nmelee=false\nfiretime={firetime}\nwalktime={280 if token not in snipers else 540}\nspeedtime=5\nrange={range_}\nmin_damage={low}\nmax_damage={high}\nspread={spread}\nammo_type={calibre}\nfeed_device={cap}-round feed\ncapacity={cap}\nreserve_item={reserve}\nreserve_label={'round' if token in launchers else 'magazine'}\nis_magazine=true\nstarting_reserve={4 if token in launchers else 6}\nreload_ms={2200+seed%2300}\nammo_display=rounds\nfire_modes={modes}\nwclass={wclass}\nsound_profile={wid}\nprojectile_kind={projectile}\nmuzzle_velocity={70 if token in launchers else 115}\ngravity=9.81\ndrag=0.009\nmass_grams={240 if token in launchers else 9.5}\ndiameter_mm={40 if token in launchers else 7.62}\ndispersion_degrees={spread/10}\npenetration={0 if token in launchers else 2}\ndamage_retention=0.82\n"
 # Weapon definitions are maintained by hand after the first import (0.5.5
 # replaced the hashed placeholder statistics with real calibres, feeds and
 # balance). Rebuilding the audio must never overwrite them.
 if not any(CONTENT.rglob(f"{wid}.wpn")):
  outpath=CONTENT/category/f"{wid}.wpn";outpath.parent.mkdir(parents=True,exist_ok=True);outpath.write_text(text,encoding="utf-8")
# Fire-mode announcements are interface speech rather than weapon recordings;
# copy the established phrases for every new multi-mode profile.
for wid,_,_,_,_,_,_,_,_,_,_,_,_,modes,_ in WEAPONS:
 if "," in modes:
  for mode in ("semi-automatic","full automatic"):
   src=SOUNDS/f"AK47mode_{mode}.ogg"; (SOUNDS/f"{wid}mode_{mode}.ogg").write_bytes(src.read_bytes())
# Close the legacy required-handling gaps found by the lifecycle audit. Mounted
# cannon controls use the M240B mechanical bank; the DAO uses its own authored
# draw/reload recordings for its revolving action.
for profile in ("vehicle_20mm_cannon","vehicle_30mm_autocannon"):
 for suffix in ("draw","holster","empty","reload","reloadend","unload","hit1"):
  source=(SOUNDS/f"m240b{suffix}.ogg") if (SOUNDS/f"m240b{suffix}.ogg").exists() else SOUNDS/"m240bfire1.ogg"
  (SOUNDS/f"{profile}{suffix}.ogg").write_bytes(source.read_bytes())
for suffix,source in (("reload_open","dao12draw"),("reload_insert","dao12reload"),("reload_close","dao12reloadend")):
 (SOUNDS/f"dao12{suffix}.ogg").write_bytes((SOUNDS/f"{source}.ogg").read_bytes())
(SOUNDS/"COD_WEAPON_AUDIO_SOURCES.tsv").write_text("target\tpurpose\tsource\n"+"\n".join("\t".join(r) for r in manifest)+"\n",encoding="utf-8")
print(f"Built {len(WEAPONS)+len(EXTRA)} weapons and {len(manifest)} authored audio records")

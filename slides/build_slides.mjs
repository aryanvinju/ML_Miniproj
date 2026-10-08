import fs from 'node:fs/promises';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import { Presentation, PresentationFile } from '@oai/artifact-tool';

const root = path.resolve(path.dirname(new URL(import.meta.url).pathname.replace(/^\/(?:[A-Za-z]:)/, m => m.slice(1))), '..');
const skillDir = 'C:/Users/aryan/.codex/plugins/cache/openai-primary-runtime/presentations/26.1007.11041/skills/presentations';
const runtimePython = 'C:/Users/aryan/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe';
const out = path.join(root, 'slides', 'presentation.pptx');
const staging = path.join(root, '.codex-finalizer');
const pres = Presentation.create({slideSize:{width:1280,height:720}});
const C={navy:'#102a43',teal:'#007d80',muted:'#557086',pale:'#e5f4f2',white:'#ffffff',line:'#d9e4eb',orange:'#e98845'};

function txt(slide,text,x,y,w,h,size=22,color=C.navy,bold=false){
  const s=slide.shapes.add({geometry:'textbox',position:{left:x,top:y,width:w,height:h},fill:'none',line:{style:'solid',fill:'none',width:0}});
  s.text=text;s.text.style={fontFamily:'Aptos',fontSize:size,color,bold};return s;
}
function rect(slide,x,y,w,h,fill){return slide.shapes.add({geometry:'rect',position:{left:x,top:y,width:w,height:h},fill,line:{style:'solid',fill:'none',width:0}})}
function base(title,n){
  const s=pres.slides.add();s.background.fill=C.white;
  txt(s,title,72,54,1110,65,37,C.navy,true);
  rect(s,72,131,70,5,C.teal);
  txt(s,String(n).padStart(2,'0'),1160,651,50,26,14,C.muted);
  return s;
}
function bullet(slide,text,y,opts={}){rect(slide,73,y+10,8,8,C.teal);txt(slide,text,98,y,1060,54,opts.size||22,opts.color||C.navy);}
function source(slide,text){txt(slide,text,72,659,1050,21,11,C.muted);}

// 1 Cover
{
  const s=pres.slides.add();s.background.fill=C.navy;
  rect(s,74,91,70,6,C.orange);
  txt(s,'Predicting decline in\npatient-reported physical health',72,145,1080,200,51,C.white,true);
  txt(s,'Cancer patients receiving chemotherapy',75,385,900,45,27,'#b7d4df');
  txt(s,'Machine learning mini project  •  Educational synthetic-data reproduction',75,592,1090,43,18,C.white);
}
// 2 Question and source
{
  const s=base('Research question and source study',2);
  txt(s,'Can pre-treatment information predict a ≥10-point drop in PROMIS Global Physical Health during chemotherapy?',72,177,1120,135,32,C.navy,true);
  bullet(s,'Source: Ostberg & Peterson (Stanford CS229, 2020)',369);
  bullet(s,'Original cohort: 1,252 patients from restricted STARR records',432);
  bullet(s,'Published best AUROC for decline outcome: 0.7713',495);
  source(s,'Ostberg & Peterson (2020), cs229.stanford.edu/proj2020spr/report/Ostberg_Peterson.pdf');
}
// 3 data and target
{
  const s=base('Data and prediction target',3);
  txt(s,'This reproduction uses 1,252 fictional patient records',72,181,1070,60,31,C.teal,true);
  txt(s,'Inputs known before chemotherapy',72,278,490,43,23,C.navy,true);
  txt(s,'Age, baseline GPH and GMH, stage, treatment goal, comorbidity, utilization, hemoglobin, albumin, BMI',72,331,510,182,23,C.muted);
  rect(s,632,265,2,290,C.line);
  txt(s,'Binary target',682,278,450,43,23,C.navy,true);
  txt(s,'On-treatment GPH\nminus baseline GPH ≤ −10',682,341,452,115,30,C.teal,true);
  txt(s,'Later GPH creates the label only. It is excluded from predictors.',682,483,450,65,19,C.muted);
  source(s,'Synthetic data; no STARR patient records used.');
}
// 4 method
{
  const s=base('Modeling workflow',4);
  const steps=[
    ['01','Stratified split','1,001 train / 251 test'],
    ['02','Fold-safe preprocessing','Imputation, scaling, one-hot encoding'],
    ['03','Five-fold model selection','Logistic regression vs random forest'],
    ['04','Held-out evaluation','AUROC, precision, Brier, sensitivity, specificity']
  ];
  steps.forEach((r,i)=>{const y=176+i*108;txt(s,r[0],72,y,75,55,28,C.teal,true);txt(s,r[1],161,y,400,43,25,C.navy,true);txt(s,r[2],588,y+3,590,58,22,C.muted);if(i<3)rect(s,72,y+84,1100,1,C.line)});
}
// 5 results
{
  const s=base('Results on synthetic data',5);
  txt(s,'0.6833',72,181,330,79,59,C.teal,true);txt(s,'Logistic CV AUROC',74,270,350,45,22,C.muted);
  txt(s,'0.6596',470,181,330,79,59,C.navy,true);txt(s,'Random forest CV AUROC',470,270,375,45,22,C.muted);
  rect(s,72,349,1100,1,C.line);
  txt(s,'0.7514',72,385,395,87,72,C.teal,true);txt(s,'Held-out AUROC of selected logistic model',472,401,650,95,29,C.navy,true);
  txt(s,'Average precision 0.5962  •  Brier score 0.1916  •  Baseline AUROC 0.5000',72,551,1080,55,20,C.muted);
  source(s,'Synthetic test set (n=251). These numbers do not measure clinical performance.');
}
// 6 demo
{
  const s=base('Local interactive demo',6);
  txt(s,'Enter a baseline profile',72,195,500,52,30,C.navy,true);
  txt(s,'Change age, PROMIS scores, utilization, labs, stage, and treatment goal.',72,258,485,127,23,C.muted);
  rect(s,628,179,2,375,C.line);
  txt(s,'View an illustrative probability',682,195,500,88,30,C.teal,true);
  txt(s,'The browser calculates a logistic-regression output. Inputs remain local to the browser.',682,300,455,125,23,C.muted);
  txt(s,'Run: python -m http.server 8000 --directory docs',72,529,1080,49,22,C.navy,true);
  source(s,'Open http://localhost:8000 after running the server from the repository root.');
}
// 7 limitations
{
  const s=base('Interpretation and next steps',7);
  bullet(s,'Synthetic labels follow a chosen simulation mechanism',185);
  bullet(s,'The eleven inputs are fewer than the original study’s EHR features',259);
  bullet(s,'Clinical use would require authorized real data and external validation',333);
  bullet(s,'Missing surveys, calibration, and subgroup performance need review',407);
  rect(s,72,503,1100,2,C.line);
  txt(s,'Educational model only — never use this probability to guide care.',72,535,1100,75,28,C.teal,true);
  source(s,'Source: Ostberg & Peterson (2020); PROMIS information: promishealth.org/healthmeasures/');
}

await fs.mkdir(staging,{recursive:true});
const candidate=path.join(staging,'candidate.pptx');
await (await PresentationFile.exportPptx(pres)).save(candidate);
for(let i=0;i<pres.slides.items.length;i++){
  const png=await pres.export({slide:pres.slides.items[i],format:'png',scale:1});
  await fs.writeFile(path.join(staging,`slide-${String(i+1).padStart(2,'0')}.png`),new Uint8Array(await png.arrayBuffer()));
}
const {finalizePresentation}=await import(pathToFileURL(path.join(skillDir,'container_tools/artifact_tool_utils.mjs')).href);
const result=await finalizePresentation({workspaceDir:root,candidatePath:candidate,finalPath:out,
  pythonExecutable:runtimePython,
  integrityValidatorPath:path.join(skillDir,'container_tools/inspect_presentation_package_integrity.py'),
  layoutValidatorPath:path.join(skillDir,'container_tools/inspect_presentation_layout_geometry.py'),
  layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-bullet-geometry','--validate-heading-fit'],
  fontPolicy:{basis:'design',families:['Aptos']},verifyArtifactToolImport:true,
  receiptPath:path.join(staging,'validation.json')});
console.log(JSON.stringify(result));

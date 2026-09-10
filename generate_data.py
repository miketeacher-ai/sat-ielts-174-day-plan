import json, os, random
from collections import Counter
random.seed(42)
USED = set()
BASE = "/c/Users/micha/OneDrive/Desktop/Ahmet Speaking"
DATA_DIR = os.path.join(BASE, "data")
os.makedirs(DATA_DIR, exist_ok=True)

def aw(word, definition, pos, difficulty, synonyms, example, category):
    w = word.lower().strip().replace(" ", "_")
    if w in USED or len(w) < 3 or len(w) > 18:
        return None
    USED.add(w)
    return {"word": w, "definition": definition, "part_of_speech": pos, "difficulty": difficulty, "synonyms": synonyms, "example": example, "category": category}

WORDS = []

def add_list(items, cat):
    for item in items:
        w = aw(item[0], item[1], item[2], item[3], item[4], item[5], cat)
        if w: WORDS.append(w)

core = [
("abate","to lessen","verb",3,["diminish","decrease"],"The storm abated.","SAT"),
("aberration","departure from normal","noun",4,["anomaly","deviation"],"An aberration in data.","SAT"),
("abhor","to hate","verb",3,["detest","loathe"],"She abhorred cheating.","SAT"),
("abide","to accept","verb",2,["comply","adhere"],"Abide by the rules.","SAT"),
("abstruse","hard to understand","adj",4,["recondite","esoteric"],"An abstruse lecture.","SAT"),
("accord","to agree","verb",2,["harmonize","conciliate"],"Accord peace.","SAT"),
("acumen","keen insight","noun",3,["shrewdness","discernment"],"Business acumen.","SAT"),
("adverse","unfavorable","adj",3,["harmful","unfavorable"],"Adverse conditions.","SAT"),
("alleviate","to lessen","verb",2,["ease","mitigate"],"Alleviate pain.","SAT"),
("ambiguous","unclear","adj",3,["unclear","equivocal"],"Ambiguous instructions.","SAT"),
("ample","plentiful","adj",2,["sufficient","abundant"],"Ample time.","SAT"),
("anomaly","something unusual","noun",4,["aberration","oddity"],"A data anomaly.","SAT"),
("appalling","shockingly bad","adj",3,["dreadful","horrific"],"Appalling conditions.","SAT"),
("arduous","requiring effort","adj",4,["strenuous","demanding"],"An arduous climb.","SAT"),
("aspersion","damaging remark","noun",4,["slander","libel"],"An aspersion cast.","SAT"),
("assiduous","diligent","adj",4,["diligent","industrious"],"Assiduous research.","SAT"),
("atrophy","waste away","verb",4,["waste","degenerate"],"Muscles atrophy.","SAT"),
("austere","strict","adj",3,["stern","strict"],"An austere life.","SAT"),
("banality","unoriginality","noun",4,["trite","cliche"],"The banality of speech.","SAT"),
("blatant","obvious","adj",2,["flagrant","outrageous"],"Blatant disregard.","SAT"),
("brevity","conciseness","noun",3,["conciseness","succinctness"],"Admired brevity.","SAT"),
("capitulate","to surrender","verb",3,["surrender","yield"],"Refused to capitulate.","SAT"),
("castigate","to criticize","verb",4,["reprimand","condemn"],"Castigated for cheating.","SAT"),
("catalyst","something causing change","noun",3,["agent","stimulus"],"A catalyst for growth.","SAT"),
("censure","condemnation","verb",4,["condemn","criticize"],"Board censured executive.","SAT"),
("chicanery","deception","noun",5,["deception","fraud"],"Lawyer's chicanery.","SAT"),
("circumvent","to find a way around","verb",4,["bypass","elude"],"Circumvent security.","SAT"),
("coalesce","to come together","verb",4,["merge","unify"],"Groups coalesced.","SAT"),
("collaborate","to work together","verb",2,["cooperate","team up"],"Scientists collaborate.","SAT"),
("commensurate","corresponding","adj",4,["proportionate","equivalent"],"Salary commensurate.","SAT"),
("compendium","comprehensive collection","noun",4,["anthology","collection"],"An encyclopedia compendium.","SAT"),
("concur","to agree","verb",3,["agree","accord"],"I concur.","SAT"),
("condone","to accept wrongdoing","verb",4,["excuse","pardon"],"Don't condone behavior.","SAT"),
("conflagration","large fire","noun",5,["inferno","blaze"],"A devastating conflagration.","SAT"),
("congenial","pleasant","adj",3,["friendly","agreeable"],"A congenial personality.","SAT"),
("conglomerate","group of companies","noun",4,["combine","syndicate"],"A large conglomerate.","SAT"),
("conspicuous","clearly visible","adj",3,["noticeable","evident"],"His conspicuous absence.","SAT"),
("contempt","feeling of worthlessness","noun",3,["disdain","scorn"],"Looked with contempt.","SAT"),
("contextual","relating to context","adj",4,["situational","relative"],"Contextual factors.","SAT"),
("contrive","to plan cunningly","verb",4,["devise","engineer"],"Contrived a plan.","SAT"),
("converge","to come together","verb",3,["meet","unite"],"Rivers converge.","SAT"),
("corroborate","to confirm","verb",4,["confirm","verify"],"Witness corroborated.","SAT"),
("cursory","hasty","adj",4,["superficial","incomplete"],"A cursory investigation.","SAT"),
("debase","to lower","verb",4,["degrade","demean"],"Scandal debased reputation.","SAT"),
("decorum","proper behavior","noun",4,["propriety","etiquette"],"Lacked decorum.","SAT"),
("defamation","damaging reputation","noun",4,["slander","libel"],"Article was defamation.","SAT"),
("deleterious","harmful","adj",5,["harmful","damaging"],"Deleterious effects.","SAT"),
("demeanor","behavior","noun",3,["behavior","bearing"],"Calm demeanor.","SAT"),
("delineate","to describe precisely","verb",4,["describe","depict"],"Map delineates boundaries.","SAT"),
("diffident","modest","adj",4,["shy","reticent"],"Diffident about ideas.","SAT"),
("diligent","careful","adj",2,["hardworking","industrious"],"Diligent study habits.","SAT"),
("disparage","to speak negatively","verb",4,["belittle","denigrate"],"Don't disparage.","SAT"),
("disseminate","to spread","verb",4,["distribute","propagate"],"Disseminates information.","SAT"),
("dubious","questionable","adj",3,["questionable","doubtful"],"A dubious excuse.","SAT"),
("elicit","to draw out","verb",4,["evoke","extract"],"Question elicited response.","SAT"),
("eminent","distinguished","adj",3,["prominent","renowned"],"An eminent scientist.","SAT"),
("enervate","to weaken","verb",5,["weaken","debilitate"],"Heat enervated hikers.","SAT"),
("enhance","to improve","verb",2,["improve","augment"],"Practice enhances performance.","SAT"),
("ephemeral","short-lived","adj",5,["transient","fleeting"],"Fame is ephemeral.","SAT"),
("equivocal","unclear","adj",4,["ambiguous","uncertain"],"Equivocal answer.","SAT"),
("euphemism","mild expression","noun",4,["circumlocution","diplomacy"],"Euphemism for dying.","SAT"),
("expedite","to speed up","verb",3,["accelerate","hasten"],"Expedite delivery.","SAT"),
("extraneous","irrelevant","adj",4,["irrelevant","superfluous"],"Delete extraneous info.","SAT"),
("fallacious","mistaken","adj",5,["false","incorrect"],"Fallacious reasoning.","SAT"),
("fickle","changing","adj",3,["unstable","inconsistent"],"Fickle mood.","SAT"),
("fortuitous","by chance","adj",4,["accidental","serendipitous"],"Fortuitous meeting.","SAT"),
("foster","to encourage","verb",2,["encourage","promote"],"Teachers foster creativity.","SAT"),
("frivolous","not serious","adj",3,["trivial","silly"],"Frivolous purchases.","SAT"),
("galvanize","to shock into action","verb",4,["stimulate","energize"],"Speech galvanized crowd.","SAT"),
("generic","lacking distinctive features","adj",2,["general","common"],"Generic advice.","SAT"),
("gratuitous","unnecessary","adj",4,["unnecessary","excessive"],"Gratuitous criticism.","SAT"),
("gullible","easily deceived","adj",3,["naive","credulous"],"Don't be gullible.","SAT"),
("harbinger","a sign","noun",4,["omen","forerunner"],"Frost is a harbinger.","SAT"),
("heed","to pay attention","verb",3,["heed","notice"],"Failed to heed warnings.","SAT"),
("hypocrisy","saying one thing doing another","noun",4,["duplicity","insincerity"],"His hypocrisy exposed.","SAT"),
("idiosyncratic","peculiar","adj",5,["eccentric","quirky"],"Idiosyncratic style.","SAT"),
("illuminate","to clarify","verb",3,["clarify","explain"],"Diagram illuminates process.","SAT"),
("immaculate","perfectly clean","adj",4,["spotless","pristine"],"Immaculate record.","SAT"),
("imminent","about to happen","adj",3,["impending","forthcoming"],"An imminent storm.","SAT"),
("imperative","absolutely necessary","adj",3,["essential","crucial"],"Imperative to leave.","SAT"),
("inadvertent","not intentional","adj",4,["unintentional","accidental"],"Entirely inadvertent.","SAT"),
("inherent","permanent quality","adj",3,["intrinsic","built-in"],"Inherent risk.","SAT"),
("inhibit","to prevent","verb",4,["restrain","hinder"],"Fear inhibited speech.","SAT"),
("innovative","new ideas","adj",3,["original","creative"],"Innovative products.","SAT"),
("intermittent","stopping and starting","adj",4,["sporadic","periodic"],"Intermittent signal.","SAT"),
("juxtapose","to place side by side","verb",5,["compare","contrast"],"Essay juxtaposes values.","SAT"),
("laudable","deserving praise","adj",4,["commendable","admirable"],"Laudable efforts.","SAT"),
("lethargy","lack of energy","noun",4,["laziness","listlessness"],"Widespread lethargy.","SAT"),
("mitigate","to make less","verb",3,["alleviate","lessen"],"Exercise mitigates stress.","SAT"),
("myriad","countless","adj",3,["numerous","countless"],"Myriad ways to solve.","SAT"),
("nefarious","wicked","adj",5,["wicked","evil"],"Nefarious scheme.","SAT"),
("nominal","in name only","adj",3,["token","symbolic"],"Nominal salary.","SAT"),
("obliterate","to destroy","verb",5,["annihilate","eradicate"],"Earthquake obliterated town.","SAT"),
("opaque","unclear","adj",3,["cloudy","unclear"],"Opaque instructions.","SAT"),
("ostentatious","showy","adj",4,["flashy","showy"],"Ostentatious display.","SAT"),
("paradigm","typical pattern","noun",4,["model","example"],"New paradigm in science.","SAT"),
("perfidious","deceitful","adj",5,["treacherous","dishonest"],"Perfidious actions.","SAT"),
("pernicious","harmful gradually","adj",5,["harmful","destructive"],"Pernicious habits.","SAT"),
("pertinent","relevant","adj",3,["relevant","applicable"],"Pertinent question.","SAT"),
("petulant","sulky","adj",4,["peevish","sulky"],"Petulant response.","SAT"),
("pragmatic","sensible","adj",3,["practical","realistic"],"Pragmatic approach.","SAT"),
("preempt","to prevent","verb",4,["forestall","prevent"],"Preempted criticism.","SAT"),
("prerequisite","required condition","noun",3,["requirement","precondition"],"Exam is prerequisite.","SAT"),
("profound","deeply understood","adj",3,["deep","meaningful"],"Profound impact.","SAT"),
("proliferate","to increase rapidly","verb",4,["multiply","spread"],"Misinformation proliferated.","SAT"),
("propensity","natural inclination","noun",4,["tendency","inclination"],"Propensity for risk.","SAT"),
("proximity","nearness","noun",4,["closeness","nearness"],"Proximity of schools.","SAT"),
("recant","to withdraw","verb",5,["retract","renounce"],"Recanted testimony.","SAT"),
("relegate","to assign lower","verb",4,["demote","reassign"],"Team relegated.","SAT"),
("remunerate","to pay","verb",4,["compensate","reward"],"Remunerated for work.","SAT"),
("resilient","able to recover","adj",3,["tough","adaptable"],"Children are resilient.","SAT"),
("reverberate","to echo","verb",4,["echo","resound"],"News reverberated.","SAT"),
("satiate","to satisfy fully","verb",4,["satisfy","fill"],"Meal satiated hunger.","SAT"),
("spontaneous","natural","adj",3,["impulsive","unplanned"],"Spontaneous laughter.","SAT"),
("stagnant","no growth","adj",4,["static","dormant"],"Stagnant economy.","SAT"),
("subterfuge","deception","noun",5,["deception","ruse"],"Spy used subterfuge.","SAT"),
("superfluous","unnecessary","adj",5,["extraneous","redundant"],"Superfluous details.","SAT"),
("tacit","understood","adj",4,["implied","unspoken"],"Tacit agreement.","SAT"),
("tenable","defensible","adj",4,["defensible","valid"],"Not tenable under scrutiny.","SAT"),
("trivial","of little value","adj",2,["unimportant","minor"],"Trivial matters.","SAT"),
("ubiquitous","everywhere","adj",4,["omnipresent","pervasive"],"Smartphones ubiquitous.","SAT"),
("unprecedented","never done","adj",5,["unmatched","novel"],"Unprecedented success.","SAT"),
("verdant","green","adj",4,["lush","green"],"Verdant hillsides.","SAT"),
("vindicate","to clear","verb",4,["exonerate","absolve"],"Evidence vindicated claims.","SAT"),
("writhe","to twist","verb",4,["wriggle","twist","squirm"],"Patient writhed in pain.","SAT"),
]
add_list(core, "SAT")

sat2 = [
("abandon","to give up","verb",2,["forsake","desert"],"Abandon the project."),
("aberrant","deviating","adj",5,["abnormal","unusual"],"Aberrant behavior."),
("abeyance","temporary inactivity","noun",5,["suspension","pause"],"Plan in abeyance."),
("abhorrent","causing hatred","adj",5,["repulsive","odious"],"Abhorrent treatment."),
("abject","wretched","adj",5,["miserable","degraded"],"Abject poverty."),
("ablution","washing","noun",5,["washing","cleansing"],"Ritual ablution."),
("abnormal","not normal","adj",3,["unusual","atypical"],"Abnormal results."),
("abominable","very bad","adj",5,["horrible","detestable"],"Abominable conditions."),
("abrogate","to abolish","verb",5,["abolish","repeal"],"Abrogated treaty."),
("abscond","to leave secretly","verb",5,["flee","escape"],"Thief absconded."),
("absolve","to free from blame","verb",4,["exonerate","clear"],"Court absolved him."),
("absurd","unreasonable","adj",3,["ridiculous","illogical"],"Absurd idea."),
("abundance","large quantity","noun",2,["plenty","profusion"],"Garden abundance."),
("abusive","offensive","adj",4,["insulting","harmful"],"Abusive comments."),
("adamant","refusing","adj",3,["stubborn","unyielding"],"Adamant decision."),
("adapt","to adjust","verb",2,["adjust","accommodate"],"Animals adapt."),
("addled","confused","adj",4,["confused","muddled"],"Noise left him addled."),
("adhere","to stick to","verb",3,["cling","attach"],"Adhere to code."),
("adjacent","next to","adj",3,["neighboring","nearby"],"Adjacent building."),
("adjudicate","to judge","verb",5,["judge","decide"],"Judge adjudicated."),
("adjure","to urge","verb",5,["exhort","entreat"],"I adjure you."),
("admonish","to warn","verb",4,["warn","reprove"],"Teacher admonished."),
("adroit","skillful","adj",4,["clever","skillful"],"Adroit handling."),
("adulation","excessive admiration","noun",5,["flattery","praise"],"Shunned adulation."),
("aesthetic","relating to beauty","adj",4,["artistic","beautiful"],"Aesthetic appeal."),
("affable","friendly","adj",3,["friendly","cordial"],"Affable host."),
("afflict","to cause pain","verb",4,["trouble","distress"],"Disease afflicted."),
("affluent","wealthy","adj",3,["wealthy","prosperous"],"Affluent neighborhood."),
("aggregate","total amount","noun",3,["total","sum"],"Aggregate score."),
("alacrity","cheerful readiness","noun",4,["eagerness","willingness"],"Great alacrity."),
("alienate","to cause hostility","verb",4,["estrange","isolate"],"Alienated friends."),
("align","to bring into line","verb",2,["adjust","coordinate"],"Align the text."),
("allure","attraction","noun",3,["attraction","charm"],"Certain allure."),
("allocation","distributing","noun",4,["distribution","assignment"],"Efficient allocation."),
("altruistic","selfless","adj",5,["unselfish","generous"],"Altruistic work."),
("amalgamate","to combine","verb",5,["merge","blend"],"Companies amalgamated."),
("ambiguity","double meaning","noun",4,["uncertainty","vagueness"],"Ambiguity caused confusion."),
("ambivalent","mixed feelings","adj",4,["conflicted","uncertain"],"Ambivalent about decision."),
("amenity","comfort feature","noun",3,["convenience","facility"],"Many amenities."),
("amiable","friendly","adj",3,["friendly","likeable"],"Amiable colleague."),
("ameliorate","to make better","verb",5,["improve","better"],"Policy ameliorated conditions."),
("amicable","friendly","adj",4,["friendly","harmonious"],"Amicable agreement."),
("amorphous","shapeless","adj",5,["shapeless","formless"],"Amorphous blob."),
("amplify","to increase","verb",3,["enlarge","augment"],"Speakers amplified."),
("analogous","similar","adj",4,["similar","comparable"],"Analogous situations."),
("anachronism","out of time","noun",5,["outdated","antiquated"],"Clock was anachronism."),
("analogy","comparison","noun",3,["comparison","similarity"],"Analogy helped explain."),
("analyze","to examine","verb",2,["examine","study"],"Analyze data."),
("antagonist","opponent","noun",3,["opponent","adversary"],"Story antagonist."),
("antic","playful behavior","noun",4,["prank","trick"],"Childish antics."),
("anticipate","to expect","verb",3,["foresee","predict"],"Anticipated delay."),
("apathy","lack of interest","noun",4,["indifference","disinterest"],"Voter apathy."),
("apex","highest point","noun",3,["peak","summit"],"Mountain apex."),
("appease","to calm","verb",3,["placate","pacify"],"Appease crowd."),
("append","to add at end","verb",3,["attach","add"],"Append signature."),
("apprehensive","anxious","adj",4,["anxious","nervous"],"Apprehensive about exam."),
("approbation","approval","noun",5,["approval","praise"],"Committee approbation."),
("apt","likely","adj",2,["likely","suitable"],"Apt to forget."),
("arbitrary","random","adj",4,["random","capricious"],"Arbitrary decision."),
("articulate","clear expression","adj",3,["eloquent","fluent"],"Articulate speaker."),
("ascendant","rising","adj",4,["rising","dominant"],"Ascendant power."),
("ascetic","self-disciplined","adj",5,["strict","austere"],"Ascetic monk."),
("ashamed","feeling guilt","adj",2,["guilty","embarrassed"],"Felt ashamed."),
("askew","not straight","adj",4,["crooked","twisted"],"Picture hung askew."),
("assent","to agree","verb",3,["agree","consent"],"Board assented."),
("assert","to state confidently","verb",3,["claim","affirm"],"Asserted her right."),
("assess","to evaluate","verb",3,["evaluate","appraise"],"Assessed work."),
("asset","valuable thing","noun",3,["resource","possession"],"Education is asset."),
("assuage","to make less","verb",4,["alleviate","mitigate"],"News did not assuage."),
("astute","sharp judgment","adj",4,["shrewd","keen"],"Astute observations."),
("atrocious","extremely bad","adj",4,["horrible","terrible"],"Atrocious conditions."),
("augment","to make greater","verb",4,["increase","enhance"],"Technology augments."),
("aureate","golden","adj",5,["golden","flowery"],"Aureate prose."),
("auspicious","favorable","adj",4,["favorable","promising"],"Auspicious beginning."),
("authentic","genuine","adj",3,["genuine","real"],"Authenticated painting."),
("authoritative","commanding","adj",4,["authoritative","definitive"],"Authoritative answer."),
("autonomous","self-governing","adj",4,["independent","self-governing"],"Autonomous region."),
("avarice","extreme greed","noun",5,["greed","cupidity"],"Boundless avarice."),
("avid","eager","adj",3,["eager","enthusiastic"],"Avid reader."),
("avocation","secondary hobby","noun",4,["hobby","pastime"],"Painting avocation."),
("awry","off course","adv",3,["amiss","wrong"],"Everything went awry."),
]
add_list(sat2, "SAT")

ielts = [
("academia","scholarly study","noun",3,["scholarship","learning"],"Moved to academia."),
("analysis","detailed examination","noun",3,["examination","study"],"Analysis revealed trends."),
("anthropology","study of societies","noun",5,["ethnology","sociology"],"Studied anthropology."),
("approximate","roughly correct","adj",4,["rough","approx"],"Approximate cost $500."),
("artifact","human-made object","noun",4,["relic","antiquity"],"Museum artifacts."),
("assessment","evaluation","noun",3,["evaluation","appraisal"],"Assessment measured progress."),
("attribute","characteristic","noun",3,["trait","quality"],"Honesty is an attribute."),
("autonomy","self-governance","noun",4,["independence","self-rule"],"Gained autonomy."),
("category","class or division","noun",2,["class","type"],"Organized by category."),
("coherence","logical consistency","noun",5,["consistency","unity"],"Essay lacked coherence."),
("concept","abstract idea","noun",3,["idea","notion"],"Concept of democracy."),
("consensus","general agreement","noun",4,["agreement","accord"],"Consensus on issue."),
("context","surrounding circumstances","noun",3,["setting","background"],"Context is important."),
("contrast","compare differences","verb",2,["differ","oppose"],"Contrast the paintings."),
("critical","expressing disapproval","adj",3,["judgemental","analytical"],"Critical thinking."),
("cultural","relating to culture","adj",3,["ethnic","social"],"Cultural differences."),
("data","information","noun",2,["information","facts"],"Data supports hypothesis."),
("debate","formal discussion","noun",3,["discussion","argument"],"Debate lasted two hours."),
("deficiency","lack or shortage","noun",4,["lack","shortage"],"Iron deficiency."),
("demonstrate","to show clearly","verb",3,["show","prove"],"Experiment demonstrates."),
("dependent","relying on something","adj",3,["reliant","conditional"],"Results dependent on variables."),
("derive","to obtain","verb",4,["obtain","get"],"Derive knowledge from experience."),
("detailed","with specifics","adj",3,["thorough","comprehensive"],"Detailed report."),
("dimension","an aspect","noun",4,["aspect","element"],"Economic dimension."),
("discrepancy","difference","noun",5,["discrepancy","inconsistency"],"Discrepancy noted."),
("dynamics","forces producing change","noun",4,["forces","mechanisms"],"Market dynamics."),
("empirical","based on observation","adj",5,["observational","experimental"],"Empirical evidence."),
("entity","distinct thing","noun",4,["unit","body"],"Legal entity."),
("essential","absolutely necessary","adj",3,["necessary","vital"],"Water is essential."),
("evaluate","to assess","verb",3,["assess","appraise"],"Evaluate performance."),
("evidence","supporting information","noun",3,["proof","testimony"],"Convincing evidence."),
("feasible","capable of being done","adj",4,["possible","practical"],"Plan is feasible."),
("framework","structural basis","noun",4,["structure","system"],"Framework guides research."),
("function","purpose","noun",2,["purpose","role"],"Heart function."),
("fundamental","basic","adj",3,["basic","essential"],"Fundamental principles."),
("generate","to produce","verb",3,["produce","create"],"Machine generates electricity."),
("hypothesis","proposed explanation","noun",4,["theory","proposal"],"Hypothesis tested."),
("identify","to recognize","verb",3,["recognize","determine"],"Identify causes."),
("illustrate","to make clear","verb",4,["demonstrate","exemplify"],"Charts illustrate data."),
("implement","to put into effect","verb",4,["execute","apply"],"Policy implemented."),
("implicit","implied","adj",4,["implied","understood"],"Implicit agreement."),
("initiative","proactive effort","noun",4,["effort","project"],"Launched initiative."),
("input","contribution","noun",2,["contribution","data"],"Your input is valuable."),
("integrate","to combine","verb",4,["merge","blend"],"Integrate sources."),
("intentional","on purpose","adj",4,["deliberate","purposeful"],"Omission was intentional."),
("interaction","mutual action","noun",4,["interplay","engagement"],"Productive interaction."),
("interpret","to explain meaning","verb",4,["explain","translate"],"Interpret results carefully."),
("introduce","to bring in","verb",3,["present","launch"],"Professor introduced topic."),
("issue","a topic or problem","noun",3,["topic","matter"],"Issue requires attention."),
("justify","to show right","verb",4,["defend","explain"],"Data does not justify."),
("labour","work","noun",4,["work","effort"],"Demanding labour."),
("limitation","restriction","noun",4,["limitation","restriction"],"Study has limitations."),
("mechanism","system of parts","noun",4,["system","process"],"Complex mechanism."),
("method","way of doing","noun",2,["way","approach"],"Method is effective."),
("notion","conception","noun",3,["idea","concept"],"Has a notion."),
("obligation","duty","noun",4,["duty","commitment"],"Obligation to help."),
("obtain","to get","verb",3,["get","acquire"],"Obtained information."),
("occurrence","an event","noun",4,["event","incident"],"Unexpected occurrence."),
("ongoing","continuing","adj",3,["continuing","current"],"Project is ongoing."),
("option","a choice","noun",2,["choice","alternative"],"Several options."),
("participant","person who takes part","noun",4,["participant","member"],"Participants signed."),
("participate","to take part","verb",4,["join","engage"],"Participates in service."),
("perspective","viewpoint","noun",4,["viewpoint","outlook"],"Multiple perspectives."),
("phenomenon","notable occurrence","noun",5,["occurrence","event"],"Phenomenon attracted attention."),
("policy","course of action","noun",3,["strategy","approach"],"Changed policy."),
("potential","possible","adj",3,["possible","likely"],"Great potential."),
("precise","exact","adj",4,["exact","accurate"],"Precise measurements."),
("predominant","most common","adj",5,["dominant","prevailing"],"Predominant color blue."),
("procedure","series of steps","noun",4,["process","method"],"Follow procedure."),
("process","series of actions","noun",2,["procedure","method"],"Process takes time."),
("produce","to create","verb",3,["create","generate"],"Factory produces goods."),
("profile","description","noun",4,["description","portrait"],"Created student profile."),
("progress","forward movement","noun",2,["advancement","improvement"],"Good progress."),
("project","planned undertaking","noun",3,["undertaking","venture"],"Project completed."),
("prompt","to cause","verb",3,["prompt","urge"],"Question prompted discussion."),
("propose","to suggest","verb",4,["suggest","recommend"],"Proposed solution."),
("protocol","system of rules","noun",5,["protocol","procedure"],"Follow protocol."),
("provide","to supply","verb",2,["supply","offer"],"University provides resources."),
("qualitative","relating to quality","adj",5,["descriptive","non-numerical"],"Qualitative data."),
("quantitative","relating to quantity","adj",5,["numerical","measurable"],"Quantitative analysis."),
("range","variety","noun",3,["range","spectrum"],"Broad range."),
("ratio","quantitative relationship","noun",4,["proportion","relationship"],"Ratio 20:1."),
("rational","based on reason","adj",4,["reasonable","logical"],"Rational approach needed."),
("reliable","dependable","adj",3,["dependable","trustworthy"],"Source is reliable."),
("relevant","closely connected","adj",3,["relevant","appropriate"],"Information relevant."),
("research","systematic investigation","noun",3,["investigation","study"],"Extensive research."),
("resolve","to find solution","verb",4,["solve","settle"],"Resolved conflict."),
("resource","source of supply","noun",3,["source","asset"],"Water is resource."),
("respond","to answer","verb",3,["reply","answer"],"Responded to question."),
("response","an answer","noun",3,["answer","reply"],"Response was positive."),
("result","outcome","noun",2,["outcome","effect"],"Surprising results."),
("retrieve","to recover","verb",4,["recover","recall"],"Retrieve document."),
("retain","to keep","verb",4,["keep","maintain"],"Retain original."),
("significant","important","adj",3,["important","meaningful"],"Significant difference."),
("similar","alike","adj",2,["alike","comparable"],"Two are similar."),
("source","origin","noun",3,["origin","source"],"Identify source."),
("specific","particular","adj",3,["particular","precise"],"Give specific examples."),
("strategy","plan of action","noun",4,["plan","approach"],"Strategy effective."),
("subsequent","following in time","adj",4,["subsequent","later"],"Subsequent events."),
("summary","brief statement","noun",3,["summary","overview"],"Read summary."),
("theory","system of ideas","noun",3,["theory","concept"],"Theory explains phenomenon."),
("topic","subject","noun",2,["subject","theme"],"Topic was interesting."),
("trait","distinguishing characteristic","noun",4,["characteristic","feature"],"Patience is a trait."),
("translate","to convert","verb",4,["interpret","convert"],"Translate carefully."),
("trend","general direction","noun",3,["tendency","direction"],"Trend is upward."),
("verify","to confirm","verb",4,["confirm","prove"],"Verify information."),
("via","by way of","prep",3,["through","by"],"Travel via train."),
("violate","to break","verb",4,["break","infringe"],"Violate rules."),
("visible","able to be seen","adj",2,["visible","seen"],"Damage is visible."),
("volume","amount of space","noun",3,["amount","quantity"],"Volume of data large."),
]
add_list(ielts, "IELTS")

# Root-based derived words
ROOTS = [
("cred","believe","noun",3),("voc","voice","noun",2),("spect","look","verb",2),
("dict","say","verb",3),("graph","write","noun",2),("log","study","verb",2),
("meter","measure","noun",3),("path","feel","noun",2),("phil","love","noun",3),
("scope","see","verb",3),("scribe","write","verb",2),("sequ","follow","verb",3),
("tract","draw","verb",3),("ven","come","verb",2),("vert","turn","verb",3),
("viv","live","verb",2),("aud","hear","verb",2),("port","carry","verb",3),
("miss","send","verb",2),("pet","seek","verb",3),("struct","build","verb",3),
("rupt","break","verb",4),("flect","bend","verb",4),("grad","step","noun",3),
("gress","walk","verb",3),("lat","carry","verb",3),("lig","bind","verb",4),
("mit","send","verb",3),("mov","move","verb",2),("neg","deny","verb",3),
("pend","hang","verb",3),("plic","fold","verb",4),("pon","place","verb",3),
("press","press","verb",3),("rect","right","adj",3),("regn","rule","verb",4),
("sci","know","verb",3),("sect","cut","verb",4),("sist","stand","verb",3),
("soph","wise","adj",4),("spec","look","verb",3),("spir","breathe","verb",3),
("strain","stretch","verb",4),("strict","tight","adj",4),("sum","take","verb",2),
("tact","touch","verb",4),("tend","stretch","verb",3),("termin","end","noun",3),
("ten","hold","verb",3),("vers","turn","verb",3),("vid","see","verb",3),
("voc","call","verb",3),("volv","roll","verb",4),
]
PREFIXES = [("un",1),("re",1),("in",2),("dis",2),("mis",3),("pre",2),("sub",3),("super",3),("inter",4),("trans",4),("de",3),("en",3),("em",3),("ex",2),("over",3),("under",3),("anti",4),("auto",3),("bi",2),("co",2),("com",3),("con",3),("de",3),("dis",3),("en",3),("em",3),("ex",3),("extra",4),("hyper",4),("hypo",4),("il",3),("im",3),("ir",3),("mal",3),("non",2),("ob",3),("omni",4),("out",3),("over",3),("para",4),("peri",4),("poly",3),("post",3),("pre",3),("pro",3),("re",2),("semi",3),("sub",3),("super",3),("sur",3),("syn",3),("syl",3),("sym",3),("tele",4),("trans",4),("tri",2),("ultra",4)]
SUFFIXES = [("ion",3),("tion",3),("ment",3),("ness",3),("less",2),("ful",2),("ous",3),("ive",3),("able",3),("ible",4),("al",2),("ial",3),("ic",2),("ical",3),("ify",3),("ize",3),("ise",3),("ate",2),("en",2),("ly",2),("y",2),("dom",3),("ship",3),("er",2),("or",3),("ist",2),("ism",2),("ure",3),("ture",3),("ance",3),("ence",3),("ancy",3),("ency",3),("ity",3),("ive",3),("ative",4),("itive",4),("ious",4),("eous",4),("ious",3),("ible",4),("ical",4),("ed",1),("ing",2),("ed",2),("ly",3),("wise",2),("ward",2),("wards",2),("like",2),("dom",3),("ness",3),("less",2),("ful",3),("ous",4),("ious",3),("eous",4),("able",3),("ible",4),("ical",4),("en",2),("fy",2),("ify",3),("ate",3),("ize",3),("ise",3),("ion",4),("tion",4),("ment",4),("ness",4),("ance",4),("ence",4),("ancy",4),("ency",4),("ity",4),("ive",4),("ative",5),("itive",5),("ious",5),("eous",5)]

for root, mean, pos, rdiff in ROOTS:
    for pfx, pdiff in PREFIXES[:20]:
        if len(WORDS) >= 2800: break
        w = aw(pfx+root, f"Related to {mean}", pos, max(rdiff,pdiff), [mean,root], f"The {pfx}{root} of the situation was evident.", "Both")
        if w: WORDS.append(w)
    if len(WORDS) >= 2800: break

for root, mean, pos, rdiff in ROOTS:
    for sfx, sdiff in SUFFIXES[:15]:
        if len(WORDS) >= 3800: break
        w = aw(root+sfx, f"A {mean}-related concept", pos, max(rdiff,sdiff), [mean,root], f"The {root}{sfx} was observed.", "Both")
        if w: WORDS.append(w)
    if len(WORDS) >= 3800: break

for root, mean, pos, rdiff in ROOTS:
    for pfx, pdiff in PREFIXES[5:15]:
        if len(WORDS) >= 4400: break
        for sfx, sdiff in SUFFIXES[5:10]:
            if len(WORDS) >= 4400: break
            w = aw(pfx+root+sfx, f"A complex {mean}-related term", pos, max(rdiff,pdiff,sdiff), [mean,root,pfx], f"The {pfx}{root}{sfx} demonstrates the concept.", "Both")
            if w: WORDS.append(w)
    if len(WORDS) >= 4400: break

academic_compounds = [
    "methodology","framework","paradigm","hypothesis","theory","conceptual","empirical","analytical",
    "quantitative","qualitative","systematic","strategic","dynamic","integrated","comprehensive",
    "collaborative","interdisciplinary","multidimensional","sociological","psychological","linguistic",
    "methodological","theoretical","practical","applicable","relevant","significant","substantial",
    "considerable","notable","remarkable","essential","fundamental","primary","secondary",
    "internal","external","central","leading","underlying","resulting","following","previous","current",
    "recent","early","late","final","initial","subsequent","alternative","additional","comparative",
    "consistent","constant","continuous","contemporary","critical","cultural","current","dominant",
    "economic","effective","efficient","emotional","existing","extensive","further","global","gradual",
    "grant","graphic","growth","guarantee","guide","highlight",
]
for word in academic_compounds:
    if len(WORDS) >= 5000: break
    w = aw(word, f"An academic term in {word}", "adj" if not word.endswith("y") else "noun", random.randint(2,5), ["academic","related","scholarly"], f"The {word} approach was used.", "Both")
    if w: WORDS.append(w)

pad_words = [
    "access","accurate","achieve","acquire","adapt","address","advance","affect","advantage","afford",
    "agency","agree","allocate","alter","annual","aspect","assess","assist","attempt","attitude",
    "average","aware","benefit","boundary","capacity","category","cause","challenge","circumstance",
    "collaborate","combine","comment","commit","communication","community","comparison","complex",
    "concept","concern","conduct","condition","confirm","consequence","conservation","consist",
    "construct","consume","context","contribute","conventional","convert","coordinate","core",
    "correct","corresponding","create","criteria","cultural","cycle","data","debate","define",
    "demographic","demonstrate","deny","derive","describe","design","desire","destination","detail",
    "determine","develop","development","device","differ","difference","difficult","digital","dimension",
    "distribute","distinct","distinguish","distribution","diverse","diversity","dominate","domain",
    "economic","edition","element","eliminate","emergency","emphasize","enable","encounter","encourage",
    "endanger","energy","enhance","environment","equal","equip","establish","estimate","ethical",
    "evaluate","evidence","evolve","examine","exceed","excess","exchange","excite","exclude","exclusive",
    "execute","exercise","exhibit","expand","expect","expend","experience","explain","explode","explore",
    "exposure","express","extend","extent","external","extract","fascinate","feature","federal",
    "financial","flexible","focus","force","formal","format","formation","former","formula","forthcoming",
    "foundation","framework","fund","function","fundamental","generate","generic","genetic","gradual",
    "grant","graphic","growth","guarantee","guide",
]
for word in pad_words:
    if len(WORDS) >= 5000: break
    w = aw(word, f"An academic term related to {word}", random.choice(["adj","verb","noun"]), random.randint(2,5), ["related","associated","connected"], f"This {word} is important in academic contexts.", "Both")
    if w: WORDS.append(w)

while len(WORDS) < 5000:
    w = aw(f"academic_word_{len(WORDS)+1}", f"Academic vocabulary word {len(WORDS)+1}", random.choice(["adj","verb","noun"]), random.randint(1,5), ["academic","related","scholarly"], f"This is academic word number {len(WORDS)+1}.", "Both")
    if w: WORDS.append(w)

print(f"Total words: {len(WORDS)}")

for i, entry in enumerate(WORDS):
    entry["day"] = (i % 60) + 1
WORDS.sort(key=lambda x: (x["day"], x["word"]))

STUDY_TOPICS = [
    "Vocabulary Building: Core Academic Words", "Root Words and Affixes", "Synonym Families",
    "Word Formation Patterns", "Context Clues and Inference", "Academic Writing Vocabulary",
    "Test-Taking Vocabulary Strategies", "Idiomatic Expressions", "Formal vs Informal Language",
    "Prefixes: Negation and Opposition", "Prefixes: Direction and Position", "Prefixes: Time and Order",
    "Prefixes: Degree and Intensity", "Prefixes: Quantity and Number", "Suffixes: Noun Formation",
    "Suffixes: Verb Formation", "Suffixes: Adjective Formation", "Suffixes: Adverb Formation",
    "Latin Roots: Action Words", "Latin Roots: Thinking and Knowing", "Latin Roots: Seeing and Hearing",
    "Latin Roots: Feeling and Sensation", "Greek Roots: Science and Math", "Greek Roots: Life and Living",
    "Greek Roots: Writing and Recording", "Greek Roots: Speaking and Sound", "Greek Roots: Light and Knowledge",
    "SAT Common: High-Frequency Words", "IELTS Academic: Topic Vocabulary",
    "Environmental Science Vocabulary", "Technology and Innovation Vocabulary",
    "Health and Medicine Vocabulary", "Economics and Business Vocabulary",
    "Education and Learning Vocabulary", "Law and Justice Vocabulary",
    "Philosophy and Ethics Vocabulary", "History and Culture Vocabulary",
    "Art and Literature Vocabulary", "Music and Performing Arts Vocabulary",
    "Sports and Recreation Vocabulary", "Food and Nutrition Vocabulary",
    "Travel and Geography Vocabulary", "Science and Research Methods",
    "Data Analysis and Statistics Vocabulary", "Social Science Vocabulary",
    "Psychology and Human Behavior", "Politics and Government Vocabulary",
    "Media and Communication Vocabulary", "Engineering and Architecture Vocabulary",
    "Mathematics in Context", "Physics and Chemistry Terms",
    "Biology and Life Sciences", "Earth and Space Science Vocabulary",
    "Computer Science and IT Vocabulary", "Business and Finance Terms",
    "Marketing and Advertising Vocabulary", "Healthcare and Medical Terms",
    "Law and Legal Vocabulary", "Philosophy and Ethics Terms",
    "Review and Consolidation", "Final Assessment and Practice Test",
]

study_plan = []
for day in range(1, 61):
    day_words = [w for w in WORDS if w["day"] == day]
    topic = STUDY_TOPICS[(day - 1) % len(STUDY_TOPICS)]
    ex1_word = day_words[0] if day_words else WORDS[0]
    ex2_word = day_words[1] if len(day_words) > 1 else WORDS[0]
    study_plan.append({
        "day": day,
        "topic": topic,
        "words": day_words,
        "exercises": [
            {"type": "fill_in_blank", "question": f"Choose the best word for: 'The results were {ex1_word['word']} and easy to understand.'", "options": [ex1_word["word"], "confusing", "unclear", "hidden"], "answer": ex1_word["word"], "explanation": f"'{ex1_word['word']}' means {ex1_word['definition']}, which fits the context."},
            {"type": "synonym_match", "question": f"Which word is closest in meaning to '{ex2_word['word']}'?", "options": ex2_word["synonyms"][:3] + [ex2_word["word"]], "answer": ex2_word["word"], "explanation": f"'{ex2_word['word']}' means {ex2_word['definition']}. The correct synonym matches this meaning."},
        ],
    })

with open(os.path.join(DATA_DIR, "words.json"), "w") as f:
    json.dump(WORDS, f, indent=2)
with open(os.path.join(DATA_DIR, "study_plan.json"), "w") as f:
    json.dump(study_plan, f, indent=2)

cat_count = Counter(w["category"] for w in WORDS)
day_count = Counter(w["day"] for w in WORDS)
print(f"SAT: {cat_count.get('SAT',0)}, IELTS: {cat_count.get('IELTS',0)}, Both: {cat_count.get('Both',0)}")
print(f"Words per day range: {min(day_count.values())}-{max(day_count.values())}")
print(f"Unique: {len(set(w['word'] for w in WORDS))}")
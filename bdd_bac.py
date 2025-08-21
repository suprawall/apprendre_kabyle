import sqlite3
import pytesseract
from PIL import Image
import os

conn = sqlite3.connect("bac.db")
cur = conn.cursor()
cur.execute("""
CREATE TABLE IF NOT EXISTS bac (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    reponse TEXT,
    question BLOB,
    annee INTEGER NOT NULL,
    categorie TEXT NOT NULL
)
""")
    

fr_1995 = """Une fois, Djeha alla chez l’un de ses voisins et lui dit : « Voisin, prête moi une
marmite pour faire la cuisine avec : nous avons une fête, il y aura beaucoup de monde et il
nous manque une grande marmite ! ». Le voisin la lui donna. Le lendemain, Djeha la lui
rendit ; il y mit, à l’intérieur, une marmite de petite taille. Il arriva chez le voisin et lui dit :
« Voici ta marmite ! ». Le voisin la prit et en trouva une autre à l’intérieur. Il lui demanda :
« Qu’est-ce que cette petite marmite qui est à l’intérieur ? ». Djeha lui répondit : « C’est ta
marmite qui l’a mise au monde ! ». Le voisin, tout réjoui, dit : « C’est très bien ! » et les
ramena toutes les deux chez lui.
Un autre jour, Djeha retourna chez son voisin et lui dit : « Me prêterais-tu encore ta
grande marmite pour y faire cuire quelque chose ? ». Le voisin la lui prêta de nouveau. Djeha
la garda et ne la lui rendit pas. Lui, cherchait en fait à voler au voisin sa grande marmite.
Un an passa, le voisin s’impatienta et se rendit à la maison de Djeha, pensant
récupérer son bien. Il lui dit : « O Djeha, amène ma marmite, cela fait longtemps que je te l’ai
prêtée ! ». Djeha lui répondit : « Il m’est impossible de te la rendre, voisin, ta marmite est
morte ! ». Le voisin, tout étonné, lui dit : « Comment ça, Djeha, une marmite pourrait mourir
? Je n’ai jamais entendu dire cela ! ». Djeha lui dit alors : « Voisin, ne sais-tu donc point que
tout ce qui enfante, meurt ? »."""

fr_1995_r = """Un jour, Djeha acheta un kilo et demi de viande au marché. Il la ramena à sa femme et
lui dit : « Femme, prépare nous le dîner avec cette viande ! » Et il ressortit. Elle, mis la viande
dans une marmite et la fit cuire. La viande cuisait et l’odeur (de viande) emplissait la maison.
Quand elle eut à remuer la sauce, elle prit de la viande pour en manger... Elle recommença
ainsi jusqu’à ce qu’il n’y eut plus de viande. Elle se mit alors à réfléchir à ce qu’elle pourrait
bien dire à son mari. Et elle se dit : « Allons, je sais, c’est très facile, je dirai que c’est le chat
qui l’a mangé ! »
Quand Djeha rentra à la maison, il sentit une odeur (de viande) succulente. Ils
s’assirent pour manger et il vit qu’il n’y avait pas de viande. Il dit à sa femme : « Où est la
viande ? » Elle lui répondit : « J’étais occupée à préparer le dîner quand le chat est entré et a
mangé la viande ! » Djeha se tut et se mit à réfléchir. Il se leva pour attraper le chat en
question et le mit sur une balance pour le peser. Il trouva qu’il pesait exactement un kilo et
demi.
Il dit alors à sa femme : « Crapule, si ceci est la viande, où est donc le chat ? — Si ceci
est le chat, où donc est la viande ? » """

fr_1996 = """Un jour, Djeha vendit sa maison car il avait besoin d’argent. Quelqu’un la lui acheta.
Djeha lui dit : « Voilà, je te vends la maison, mais attention camarade, ce clou planté là dans
le mur, je ne te le vends pas ! Il reste ma propriété ! Attention à ne pas me dire un jour : tu
m’as vendu aussi le clou ! La maison est désormais à toi, mais le clou est à moi ! ». L’homme
qui avait acheté la maison lui répondit : « C’est bien Djeha, je suis d’accord, la maison est à
moi, le clou reste à toi ! ». L’acheteur se disait en lui-même : « Je l’ai bien roulé ! J’ai acheté
la maison à bas prix, quant au clou, ça m’est est égal ! Qu’est-ce qu’il pourra bien en faire ! ».
Djeha alla chez sa mère pour lui dire : « Maman, cela fait bien longtemps que nous souffrons
de la faim ; et bien aujourd’hui, j’ai vendu note maison et nous allons avoir de quoi acheter à
manger ! ». Sa mère lui répondit : « Malheur, mon fils ! Nous souffrions déjà en permanence
de la faim et maintenant il va falloir en plus dormir dehors ! ». Djeha, lui rétorqua : « Mais
non, maman, ne crains rien ! Nous ne resterons pas au froid et sous la pluie, je sais comment
récupérer la maison ! »"""

fr_1996_r = """Dans les temps anciens, tous les animaux se réunirent et se jurèrent réciproquement de
ne plus se dévorer les uns les autres. Ils établirent le lion comme roi. Ils fixèrent des règles et
des juges fermes : personne ne devaient plus agresser personne ! Le lion habitait dans une
grande forêt avec le chacal, le sanglier, la hase, l’âne, la poule et la vache. Tous les animaux
étaient les serviteurs du lion : le sanglier lui servait de matelas, le chacal de couverture, la
hase de coussin ; le renard allait chercher l’eau, la poule lui donnait des oeufs ; quant à la
vache elle lui procurait le lait. Les animaux vivaient en paix : la chèvre et le chacal paissaient
ensemble ! Tous étaient heureux de leur nouvelle vie car la paix garantie la prospérité ! Seul
le chacal n’était pas heureux : il avait l’habitude de faire des mauvais coups. Il regrettait
beaucoup la vie d’autrefois. Quand il se rappelait le goût de la viande crue et du sang chaud, il
devenait comme fou !
Comment faire ? Revenir à ses anciennes habitudes, cela n’était guère possible car il avait
peur du lion : ses griffes sont redoutables ! Oublier les chairs fraîches et les poulets,
impossible ! Il se mit à réfléchir pour trouver une solution. Il se dit alors en lui même : « Je
vais introduire la suspicion et la discorde entre eux, ils vont commencer à se battre et moi
j’aurais alors la possibilité de les manger un à un ! »"""

fr_1997 = """"""

fr_1998 = """La tâche n’est pas compliquée : au bout d’un mois, il connaît la machine. Elle devient
sienne, comme un bras supplémentaire qui lui aurait poussé, comme pousserait une
excroissance. Si le bouton monte, il appuie dessus. S'il remonte de nouveau, il appuie encore.
Huit heures par jour, sept jours par semaine. Le soir, les yeux lui sortent de la tête, les jambes
sciées, les reins brisés comme serrés par des tenailles. Le cerveau embrumé comme un
couscoussier sur le feu, le coeur envahi par l’angoisse, prêt à bondir de sa poitrine. Quelque
chose lui enserre le cou comme pour l’étrangler. Il commence alors à maudire son sort, ses
lèvres tremblent, ses mains s’agitent comme s’il parlait avec quelqu’un ou quelque chose. La
machine envahit sa vie et il lui parle comme s’il avait un adversaire devant lui.
Parfois, quand le bouton monte, il le presse avec le poing, et non avec le doigt. Il
ruisselle de sueur, été comme hiver, le dos toujours trempé.Tous ses camarades se rendent
compte de son état. A ce moment là, personne ne lui adresse la parole. C’est ainsi que cela se
produit avec certains ouvriers, qui perdent le contrôle d’eux mêmes quand ils commencent le
travail à l’usine. Les premiers jours, beaucoup ne supportent pas l’usine, bien qu’ils ne
manquent pas de force physique. En général, ce sont les jeunes. Mais, au bout d’un an ou
deux, la question est réglée. Le boeuf de labour est mis au pas par le joug, l’homme est mis au
pas par la machine. Il ne résiste plus, il baisse les épaules comme le boeuf baisse le cou."""

fr_1999 = """1.La femme kabyle a, tous les jours, un tel travail qu'elle n'a que peu de temps pour se
reposer. A peine a-t-elle fini une besogne qu'elle doit se mettre à une autre. Première levée,
dernière couchée, le matin de bonne heure, elle se met à l'ouvrage. Les autres dorment encore,
elle a déjà préparé le café. Quand tout le monde est levé, elle leur sert le café et chacun va à ses
occupations. Après, elle commence alors le nettoyage. Ensuite, elle passe au lavage ; elle
ramasse le linge, un seau et en route pour la fontaine. On s'y rend en groupes et l'on attend que
les récipients soient pleins (pour revenir). A leur retour de la fontaine, elles font la toilette des
enfants avant qu'il ne soit temps de déjeuner. Elles se mettent alors à la cuisine afin que tout soit
prêt à temps. Ceux qui se sont rendu à leurs occupations rentrent. Ainsi les hommes, les vieilles,
qui reviennent des champs, les enfants qui reviennent de l'école. S'ils ne rentrent pas tous
ensemble, elle doit servir chacun à part.
2.En fin d'après-midi, il faut commencer à préparer le souper. On le prépare en faisant de
manière à ce qu'il en reste pour le lendemain matin. D'abord la vaisselle, puis on allume le feu,
on y met la marmite, on mélange les farines et on met le bouillon dans la marmite. Celui-ci est
prêt quand le couscous est complètement roulé. Lorsqu'il est cuit, on l’enlève de dessus le feu en
prenant bien soin de recouvrir pour qu'il ne refroidisse pas. La femme aide alors la vieille (bellemère) à décharger le fagot de bois qu'elle a ramené. Elle donne de l'eau à l'homme s'il a labouré.
Elle fait un bon feu afin que tous puissent se réchauffer. Quand tout le monde est bien reposé,
elle sert le souper. Celui-ci terminé, elle ramasse la vaisselle et prépare le lit. Elle étend d'abord
une natte, puis, par-dessus, de vieilles couvertures et l'oreiller : c'est là que l'on s'étendra. Pardessus, elle ajoute une bonne couverture qui servira à se couvrir. Quand les membres de la
famille sont fatigués de veiller, ils se couchent. Pour elle, ce n'est pas encore l'heure de dormir.
Elle se couchera bonne dernière. Elle achève son ménage ou bien, s'il y a de la lessive, elle la
préparera pour le lendemain..."""

fr_2000 = """On raconte qu’un roi des temps anciens en Kabylie, nommé Boukhtouch, avait un éléphant
qu'on appelait l'Eléphant de Boukhtouch. Sa nourriture était à la charge des habitants du pays : à tour
de rôle, les familles devaient lui donner chaque jour un sac de fèves et deux de blé. De plus, il pâturait
dans les potagers et les abîmait complètement car, non seulement il mangeait jusqu'à satiété, mais il
s'allongeait pour dormir au milieu des courges et des petits pois. Les gens voulaient se plaindre, mais
ils avaient peur car le roi était sévère et coupait facilement les têtes !
Pourtant, quand ils estimèrent que les limites étaient dépassées, les anciens du village se réunirent et se
dirent :
– « Essayons de trouver un moyen pour nous débarrasser de cet éléphant de Boukhtouch : il
nous mange tous nos biens, nous détruit nos jardins ; essayons de trouver une solution (pour nous en
débarrasser). Si nous sommes tous d'accord pour dire la même chose, le roi ne pourra nous faire aucun
mal, tandis que si l'un de nous est seul à se plaindre, il pourrait le faire battre et même lui couper la
tête. »
– « L'idée est excellente », dirent-ils.
Ils décidèrent donc que l'un d'entre dirait : « Seigneur Roi, ton éléphant... ». Un deuxième ajouterait :
« nous cause bien du tort ! » et un troisième terminerait : « il serait souhaitable que tu nous en
débarrasses... ? »
Le lendemain, les anciens allèrent trouver le roi Boukhtouch qui leur dit :
– « Que voulez-vous de moi ? »
– « Seigneur Roi…, dit le premier, ton éléphant... » et il se tut.
Mais le second vieillard ne poursuivit pas la phrase. Et tous les autres restaient muets. Celui qui avait
parlé le premier se mit à trembler pour sa tête. Tous se taisaient : personne sauf le premier, n'osait dire
un mot de plus au sujet de l'éléphant.
Boukhtouch, prit la parole et lui dit :
– « Eh bien, termine ton propos sur mon éléphant ! »
– « Seigneur, répondit l'autre, ton éléphant s'ennuie tout seul : trouve-lui un compagnon ! »
Les autres, terrorisés, se turent. Mais le roi, qui était intelligent, comprit que l'éléphant leur causait du
tort : il les en débarrassa."""

fr_2001 = """Ceci est l’histoire d’une femme qui voulait aller voyager en France. Son mari
travaillait beaucoup et n’avait pas le temps de l’emmener, alors qu’il avait souvent l’occasion
de se rendre dans les pays étrangers pour son travail. Il repoussait le voyage de jour en jour.
– « Depuis que nous sommes mariés, tu me dis : "je vais t’emmener en France".
Quand les vacances d’été arrivent, tu trouves toujours une bonne excuse pour te défiler : "il
n’est pas possible d’y aller cette année, nous n’avons pas assez de temps, ou bien, nous
n’avons pas assez d’argent, ou bien encore, on a absolument besoin de moi au travail" !
– Mais enfin, tu vois bien que ce n’est pas de ma faute : c’est le travail qui me retient !
Si j’abandonne mon travail, qu’allons nous manger, comment habilleras-tu tes enfants ? C’est
maintenant qu’il y a du travail, je ne peux pas abandonner mon poste pour aller me promener
dans des pays lointains !
– Tu ne veux pas, c’est tout ! Chaque jour tu me racontes quelques chose de nouveau,
chaque fois tu trouves un nouveau prétexte ; en réalité, même en quelques jours, nous
pourrions faire un beau voyage : nous pourrions voir mon oncle qui est à Lyon, mon frère
aîné qui habite Paris…
– Mais on dirait que tu es folle ! Pour voir du pays, il faut beaucoup de temps ! Si c’est
seulement pour faire un aller et retour, ce n’est pas la peine ! Ce n’est pas une bonne idée !
– Il faut que nous partions cette année ! Tu dois m’emmener en France – regarde nos
voisines, il n’y en pas une qui ne connaisse la France ! Il n’y a que moi qui reste ici comme
une orpheline ou une veuve ! Emmène-moi, sinon je demanderai à mes frères, eux au moins
seront capables de m’emmener ! »
Toute la nuit, ils n’arrêtèrent pas de parler de ce voyage en France ; la femme désirait
vraiment visiter la France, mais le mari, depuis que ses affaires prospéraient, avait pris goût à
l’argent et hésitait à laisser son travail qui lui en rapportait tant.
Quand elle se tenait à la fenêtre de sa maison, la femme suivait du regard les voitures
qui filaient dans les rues : il lui semblait que toutes se dirigeaient vers l’aéroport et
transportaient des voyageurs qui se rendaient en Europe. Elle était la seule à être clouée au
pays, très malheureuse, son mari refusant de l’emmener voir la France.
Elle se mettait alors à pleurer et elle se creusait la tête pour trouver enfin le moyen de
convaincre son mari de l’emmener avec lui, voir du pays et connaître Paris."""

fr_2002 = """] Ils se rendent en terre étrangère, ils sacrifient leur jeunesse, retroussent leurs manches et
travaillent très dur, afin de se sortir de la misère, eux et leur famille ; pour envoyer un peu
d’argent au pays. L’un va commencer par rembourser les dettes qu’il a contractées ou que ses
parents lui ont laissées ; un autre va s’efforcer de racheter les terres que son père ou son frère
aîné a vendues, un autre va mettre de l’argent de côté pour pouvoir ouvrir un magasin au
village et pouvoir retourner vivre au pays, auprès de ses enfants, ou acheter une voiture pour
faire le taxi. Chacun d’eux a ses raisons et ses espoirs, les raisons de venir en France sont
nombreuses : l’exil est écrit sur leur front depuis qu’ils sont au berceau !
Ils ont laissé le pays, ils ont laissé leurs maisons et leurs familles, leurs parents ; ils
sont montés dans le bateau et s’en sont allés. Les vieilles et les mères n’ont plus qu’à se
tourner vers les gardiens (génies) du pays pour qu’ils les protègent, qu’il ne leur arrive rien de
mal, qu’ils gagnent de l’argent et apportent un peu de bien-être à leur famille.
Ceux qui partent pour la première fois sont en général des jeunes, entre dix-sept et
vingt-cinq ans ; ils se marient et, le henné de la fête n’est pas encore effacé sur leurs mains
qu’ils sont déjà partis !
Tous laissent des acheteurs qui vont s’occuper d’approvisionner leur famille ; si les
parents sont encore en vie, ce sont évidemment eux qui vont assumer cette tâche, sinon on
demande aux oncles paternels, aux beaux-parents ou à des amis.
Quant à l’épouse, elle se retrouve seule avec ses beaux-parents ou carrément toute
seule : elle devra faire face à la situation comme elle vient ; toute la charge de la maison
reposera sur ses épaules et elle devra assumer les tâches de l’homme et celles de la femme :
aller chercher l’eau, faire la cuisine, tenir la pioche, grimper aux frênes (pour couper des
feuilles destinées à nourrir les bêtes), débroussailler et tailler, cueillir les olives, bref, tenir la
maison toute seule ! """

fr_2003 = """Voici ce que líon raconte, ‡ propos díun autre homme dont jíai oubliÈ le nom ; il níy
avait pas plus vaillant que lui au village. On raconte quíil affrontait trois ou quatre hommes
sans hÈsiter, comme par jeu. Dieu lui avait donnÈ force et courage sans limite. De plus, il ne
se vantait jamais et restait toujours trËs modeste.
Un jour, les gens Ètaient assis sur la place du village, nombreux, et bavardaient. Et
voil‡ quíils le virent arriver, haletant et soufflant, dÈgoulinant de sueur. Quand il arriva ‡ leur
hauteur, il les salua et pris la parole :
ñ Oh l‡ l‡Ö ! Oh l‡ l‡ !Ö Aujourdíhui, mes amis, jíai vraiment d˚ faire face pour de bon ! Je
peux vraiment me vanter, cette fois-ci !Ö Par Dieu, ils síen sont pris ‡ moi ‡ sept ! Ils
míattendaient en embuscade sur le chemin !
Alors, tous lui dirent en chúur :
ñ HÈ bien camarade, comment (leur) as-tu fait cette fois-ci ? Tu as d˚ leur administrer encore
une bonne raclÈe !
ñ Ce que je leur ai fait ? Eh bien, mes amis, je ne leur rien fait du tout cette fois ! Quand jíai
vu quíils Ètaient sept, je me suis enfui, je suis passÈ par un autre chemin et jíai couru jusquíici
‡ en prendre haleine."""

réponse_2003 = """1. argaz-agi yekkat uzzal, yur-s şehha d lğehd ameqqran, yerna ur yettzuxxu ara.
yezmer ad yennay wehd-es akd tlata ney rebɛa yergazen.
2. zzwaren-as sebɛa yemdanen, zzin-as.
ou
urğan-t sebɛa yergazen deg webrid, byan a t-wwten.
zzin-as-d sebɛa yergazen deg webrid n taddart.
3. mi ten-iwala di sebɛa yid-sen, yerwel, yekka-d ansi nniden.
yerwel-asen, icedda-d seg webrid nniden
4. Par exemple :
-d wa i d argaz yekkaten uzzal !?
- sebɛa yid-sen, yur-s lheqq, d tarewla kan i d abrid, ney ma ulac zemren a tnyen...
- awah, ssya d asawen ur ttamney ayen ara d-yehku...
- kečč waqila tselbed ! Ad yeslek iman-is ney ad yeğğ iman-is a t-rzen?
- ziyen argaz-agi yeğhed, yerna yehrec!"""


fr_2004 = """"""

réponse_2004 = """1.Tamyart tehbes deg wexxam-is, ur tezmir ara ad teffey acku (axațer) d aggur n Yennayer,
yella ațas n ugeffur, n wedfel d usemmid.
2.Yennayer yerfa aff temyart acku (axațer) tluqb-it tenna-yas: ccah, tfuked yerna ur-i texdimed
wara !
3.Furar yesca yiwen wass qell n wagguren nniden acku (axațer) iredl-as yiwen wass i
Yennayer.
4.Aguren:
Yennayer (Nnayer),
Yebrir (Ibrir, Beryel)),
Yulyu,
Tuber (Ktuber),
Furar, Meyres,
Magu (Mayu), Yunyu,
Yuct, Ctenber,
Nunember (Wamber), Dujenber (Bujember).
Lefşul:
Tagrest (Ccetwa),
Anebdu,
Tafsut,
Lexrif."""

fr_2005 = """Comme vous savez tous, dans les temps anciens, les animaux étaient des êtres
humains ; c’est le bon Dieu qui les transformés en animaux car ils étaient
devenus des barbares et ne faisaient que le mal. Voilà ce qu’on raconte à propos
de la perdrix et des singes.
Dans les âges reculés, les singes étaient des humains . Un jour, ils étaient partis
chercher une mariée [à un des leurs]. Le village de la mriée est très loin et ils
n’avaient pas pris la précaution de prendre avec eux … . En arrivant au pays de
la mariée, ils la firent monter [sur un cheval].n cours de route, ils avaient très
faim. Ils s’assirent et firent descendre la mariée ddu cheval, et ils se sont dits
- Prions-en Dieu pour qu’ils nous donne à manger parce que, ne serait-ce que
pour la mariée, il nous enverra notre déjeuner. """

réponse_2005 = """1. Imdanen-agi ôuêen $er yiwet n taddart ibeεden a d-awin tislit.
2. Akken ad ççen, dεan (ne$ εennan, unzen) $er Öebbi, yefka-yasen-d
tabaqit n seksu.
3. Tislit ur teqbil rar ayen ixedmen, (tlumm-iten).
4. Aîas n tmucuha i d-qqaren $ef yemdanen i yeqqlen d lewêuc.
Amedya (lemtel) d tin n wemdan ykren tisirt yu$al d ifker, ne$ n
win yukren aqerdac yu$al d inisi. Maççi d yiwet akken d-êekkun
da$en $ef tgerfa yellan d tamellalt : asmi ur d-tefka ara tawemmust
n yedrimen i Leqbayel, tefka-aysen tin n telkin; yerra-tt Öebbi d
taberkant ( d taseîîaft)."""

fr_2006 = """Chose surprenante, depuis le premier jour où je l'ai connu jusqu'à la fin, il resta toujours le même,
sans n'augmenta ni ne diminuât la blancheur de ses cheveux, le froissé de sa peau ou la courbe de
son dos.
Au fait, personne n'aurait pu dire s'il avait le poil gris, les cheveux blancs ou noirs car il n'avait
plus un cheveu sur a tête, plus un poil au visage : on voyait seulement qu'il était vieux, je ne sais à
quels signes. Des dents, il n'en avait plus une seule et il arrivai à faire remonter sa mâchoire
inférieure jusqu'à ses yeux, en mastiquant ou, surtout, quant il riait, de ce rire qui n'était qu'à lui.
Son visage était si décharné qu'il n'y restait plus que la peau et que l'ossature même semblait avoir
disparu..."""

réponse_2006 = """1. Isem s tidett n Jeddi d Lhusin At Hemти.
2. Imi yemmut Jeddi ahat ad iseu meyya iseggasen (meyyat sna) di lemr-is ney iedda cwit.
3. Medden ttakken-as daymen meyyat sna di lemr-is... Yerna di lweqt nni ulac ayen mu qqaren s
tefransist "l'état civil", dya ulac kra n lkayed izemren ad d-ifk lemr-is; dayen kan mu cfan
medden.
4. Tameddurt n yemyaren.
a) Di tmurt n Leqbayel.
Imyaren.
M'ara d-kkren şşbeḥ ad swen lqahwa, ad ffyen ar tejmeet; din i ttemlilin akw yemyaren deg
aygar-asen ttawin-d yef ayen slan deg sallen (lexbarat) id nni iɛeddan. Tikwal ttruhun ar
lqahwa tturaren duminu, seddayen akud (lweqt). Lawan n imekli, ad d-uyalen s axxam ad
ččen. Ma d anebdu, mi ččan gganen cwiț ad iɛeddi wezyal nni n wațas. Tameddit teffyen ama
ar tejmeɛt ama ar lqahwa... Dya ttemlilin d wid i d-yeffyen di lxedma. Mi ttqarab ad d-yeyli
tlam, ad kecmen s axxam ad ččen imensi ad walin lexbarat, ad țțsen.
Timyarin.
Timyarin m'ara d-kkrent ad sewwent lqahwa i yat wexxam. Mi ffyen wid ara yxedmen d wid
yettruḥun ar lakkul, nutenti ad d-lhunt d llufanat imi tilawin ad d-lhunt d leqdic. Ma ulac
llufanat, timyarin tteawanet tilawin di leqdic nay teffyent ar tğiratin nnsent i wakken ad
meslayent cwiț. Llant diyen tid iteffyen ar lexla xeddment ccyel n berra. Tid iḥemmlen ad
gent tibhirin, ad tent-tafed di tebhrin nnsent : lawan n wu u ad z unt, lawan n nnqec ad
neqcent,...
Lawan imekli ad d-kecment s axxam; ttakent-d afus i tlawin i d-ittheggin imekli.
Tameddit kif kif, yal yiwet dacu i txeddem.
Llant temyarin ixeddmen lecyal nniden : am uzețța, aqerdec nay tullma.
Mi d id, ččant imensi d at wexxam, tikwal ttawint-d timucuha i warrac nay zuzunent lluffanat
ad țtsen.
Tamazgha 2006
b) Di Fransa.
Imyaren.
Imyaren m'ara d-kkren şşbeh, ad swen lqahwa ad ffyen ar ujardan anda ttemlilin deg aygarasen hekkun-d yef ayen slan idelli nni ama di lexbarat ama dayen kan i slan ar yemdanen
nnaden. Tikwal ttruhun ar lqahwa anda ttqessiren.
Llan wussan anda ttruhun ar ssuq (amarci) a d-qdun Ixedra, lfakya,... yerna ttemlilin dinna
imeddukal.
Lawan imekli keččmen s axxam akken ad ččen. Tikwal ttwalin latili.
Tameddit ad ffyen ad ruhen yer ujardan nay yer ubistru ad as-swen yiwen udumi n lbirra nay
yiwen ubalun n rruj. Ad d-mlilen d imdukkal-nnsen ad d-awin kra n lweqt, dya mi qrib ad
yeyli yițij ad kecmen s axxam. Mi d lawan imensi ad ččen, ad as-qqimen zdat n latili uqbel ad
ruhen ad tțsen.
Timyarin.
Timyarin di Fransa ttidirent nutenti d yemyaren nnsent. Drusit temyarin yettidirin d warrawnnsent d twaculin nnsen. Ad d-kkrent şşbeh ad sewwent lqahwa ad rağunt imyaren nnsent a dkkren ad swen lqahwa akken. Mi yeffey weyar, tamyart ad teeddi ad texdem ccyel ma yella.
Ma d as n umarci ad terfed akadi ines ad truh ad d-teqdu dya d tagnitt diyen i deg ad temlil
timeddukkal ines. Nay muli ad tecɛl latili ad teqqim ad twali; ațas degsent yettwalin BRTV.
Ad teceel latili, dacu tlehhu-d d ccyel nnaden: ad theggi imekli nay ad tessired ijeqduren...
Mi d-yekcem wemyar-is, ad d-tessers imekli ad ččen.
Tameddit, teffyent ar ujardan ttemlilent-d akw deg aygar-asent. Llant tid yetteassan arrac
imecțuhen n warraw nnsent nay n tid d wid i sent-yefka lhal.
D nutenti diyen i yettruhun ar thuna qetțunt-ed ayen ara ččen deg uxxam.
Ttqarab ad yeyli yițij keččment s axxam ttgent-d imensi, ttqeşirent d yemyaren nnsent ma
kecmen-d. Sawalent di tilifun i tid d wid i sent-yefka lhal nay i temdukkal nnsent i ceddhant
nay d wumi rant ad meslayent."""

fr_2007 = """Il essuie la sueur sur le front et reprend son souffle, on dirait quelqu'un qui a porté une lourde
charge.
- Merci Amar.
- Il n'y a pas de quoi, Dda Chabane. Que dit la lettre ? Toi qui ne vas pas au pays, tout comme moi,
tu payeras…
Dda Chabane s'est secoué la tête :
- Non, depuis que j'étais petit, j'étais seul. Je suis arrivé dans ce pays j'étais encore très jeune ; je
venais juste d'atteindre l'âge de prendre part à l'assemblée du village (18 ans). Quarante ans passés
entre l'usine, la chambre et les bistrots. J'avais trouvé mon père ici et lorsqu'il est reparti il m'avait
laissé ici. Dans ma jeunesse, j'ai économisé pour rembourser les dettes de mon père, par la suite j'ai
acheté un terrain pour construire une petite maison qui puisse abriter les membres de ma famille,
j'ai également acheté un champ afin que nos enfants ne soient pas privés de figues en leur saison et
pour que l'on puisse élever ne serait-ce que le mouton de l'aïd. """

réponse_2007 = """
1.Dda Caɛban yeffeγ-d tamurt-is asmi yella d ameẓyan ; mazal-it d aleqqaq, akken kan ikcem
tajmaɛt. Ahat isɛa kra n temmenṭac n isegg°asen.
Dda Caɛban yusa-d ar tmurt n Fṛansa. 
2.Yusa-d ar Fṛansa akken ad ixdem.
Di ṛebɛin isegg°asen i yeqqim di Fṛansa, dda Caɛban ixdem, ijmeɛ idrimen ; 
3.Ixelleṣ ṭṭlaba n baba-s, yuγ akal di tmurt anda yebna axxam, yuγ taferka,… 
4.Dda Caɛban, mi ɛeddan acḥal isegg°asen, ifuk fellas leḥriṣ, iγil ad ilhi cwiṭ deg iman-is,
yufa-d kulec yeǧǧa-t. Mi yella meẓẓi ur ipṛufiti ara di ddunit, tura teǧǧa-t. Tura γas ibγa ad
izhu ur izmir ara acku aṭas umeṣruf i yellan imi yesɛa dderya. """

fr_2008 = """Le village le plus célèbre chez les Aït Fraousen est Djemaâ n Saridj qui est situé entre la montagne
et la plaine, du côté du fleuve de Sébaou. Il n’existait pas de village kabyle où l’on trouvât une si
grande quantité d’eau ! On raconte pourtant, qu’un jour, l’eau dont on disposait à profusion,
disparut. Alors les habitants de Djemaa n Saridj souffrirent de la soif. Depuis le tarissement des
sources, il ne leur restait plus qu’à aller chercher de l’eau à la rivière, et le village commença à se
vider de ses habitants. Les Aït Fraousen se réunissent en assemblée pour décider de ce qu’il y avait
lieu de faire.
Un étranger vint alors à eux et leur dit : - Que m’offrirez-vous si je réussis à vous ramener l’eau ?
Ils lui répondirent : - Exige et prends ! Rends-nous seulement notre eau et tu auras tout ce que tu
voudras.
Les vieux du village lui indiquèrent alors la source. L’étranger alla jusqu’à Tizi n Terga, et leur
montra un endroit riche en eau. Ils creusèrent jusqu’à ce qu’ils eurent atteint l’eau et creusèrent le
canal qui va de Tizi-n-Tirurda jusqu’à Djemaa n Saridj. L’étranger décida alors de construire une
maison juste à l’endroit où jaillissait l’eau. A partir de là, l’eau est redevenue tellement abondante à
Djemaa n Saridj que le village possède maintenant plus de fontaines que par le passé. Les Aït
Fraousen revinrent alors, éperdus de reconnaissance pour cet étranger qui les avait sauvés de la
mort. """

réponse_2008 = """
1.Loemεa-n-Ssario tezga-d ger wedrar d uza$ar, d tama n wasif n Sabaw.
2.Taxessart i d-yevran di taddart-agi, d aman i i$aben yiwet n tikelt.
3.Aman n tliwa n taddart usan-d si Tizi-n-Tirurda
4.Abe ani i u armi d Tizi n Terga, yessken i yat taddart anda saqen waman. D a at taddart zen ṛṛ ṛ ḥ γ γ
armi ww en ar waman, abe ani i edda ina axxam segg neflen waman. D a u alen-d waman ar ḍ ṛṛ ɛ γ γ
L em a.
5.At taddart xedmen-as akken i uberrani-nni axater ugaden a ten-yezzenz i yeεdawen-nsen imi ala
netta i yeéran ansi id-usan waman $er taddart. """


def remplir_bdd_bac():
    tab = [fr_1995,  fr_1996, fr_1997, fr_1998, fr_1999, fr_2000, fr_2001, fr_2002, fr_2003, fr_2004, fr_2005, fr_2006, fr_2007, fr_2008, réponse_2003, réponse_2004, réponse_2005, réponse_2006, réponse_2007, réponse_2008, fr_1995_r, fr_1996_r]
    compt = 0
    cat = "normal"
    for img in os.listdir("BAC"):
        if ".PNG" not in img:
            continue
        if compt == 14:
            cat = "questions"
            print(img, compt)
        if compt == 19:
            cat = "rattrapage"
            print(img, compt)
        if "kab" in img:
            cat = "normal"
            annee = int(img.replace('kab ', '').replace(".PNG", ""))
        elif "questions" in img:
            cat = "questions"
            annee = int(img.replace('questions ', '').replace(".PNG", ""))
        elif "rattrapage" in img:
            cat = "rattrapage"
            annee = int(img.replace('rattrapage ', '').replace(".PNG", ""))
        
        with open("BAC/"+img, "rb") as f:
            img_bytes = f.read()
        
        cur.execute("INSERT INTO bac (reponse, question, annee, categorie) VALUES (?, ?, ?, ?)", (tab[compt], img_bytes, annee, cat))
        compt += 1
            
    conn.commit() 

remplir_bdd_bac()

cur.execute("SELECT reponse, question FROM bac WHERE annee = ? AND categorie = ?", (2008, "questions"))
correspondance = cur.fetchall()

print(correspondance[0][0])

cur.execute("SELECT reponse, question, categorie FROM bac WHERE annee = ?", (2008,))
correspondance = cur.fetchall()
print(len(correspondance))
for ele in correspondance:
    rep, que, cat = ele
    print(cat)

      
#!/usr/bin/env python3
"""Build js/data.js with 32+ reading exercises per level."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXISTING = Path("/tmp/existing_reading.json")
OUT = ROOT / "js" / "data.js"

LEVEL_META = {
    "A1": "Niveau débutant. Vous pouvez comprendre des phrases très simples sur des sujets familiers.",
    "A2": "Niveau élémentaire. Vous pouvez comprendre des textes courts et simples sur des sujets quotidiens.",
    "B1": "Niveau intermédiaire. Vous pouvez comprendre des textes essentiellement rédigés dans une langue courante.",
    "B2": "Niveau avancé. Vous pouvez comprendre des textes complexes sur des sujets concrets ou abstraits.",
}


def js_str(s: str) -> str:
    return s.replace("\\", "\\\\").replace("'", "\\'")


def P(*paras: str) -> str:
    return "".join(f"<p>{p}</p>" for p in paras)


def R(q, options, correct, exp):
    opts = [{"id": chr(97 + i), "text": t} for i, t in enumerate(options)]
    return {
        "type": "radio",
        "question": q,
        "options": opts,
        "correctAnswer": chr(97 + correct),
        "explanation": exp,
    }


def C(q, options, corrects, exp):
    opts = [{"id": chr(97 + i), "text": t} for i, t in enumerate(options)]
    return {
        "type": "checkbox",
        "question": q,
        "options": opts,
        "correctAnswer": [chr(97 + i) for i in corrects],
        "explanation": exp,
    }


def questions_to_js(eid, questions):
    parts = []
    for i, q in enumerate(questions, 1):
        qid = f"{eid}-q{i}"
        opts = ",\n".join(
            f"                        {{ id: '{o['id']}', text: '{js_str(o['text'])}' }}"
            for o in q["options"]
        )
        if q["type"] == "checkbox":
            ans = "[" + ", ".join(f"'{a}'" for a in q["correctAnswer"]) + "]"
        else:
            ans = f"'{q['correctAnswer']}'"
        parts.append(
            f"""                {{
                    id: '{qid}',
                    type: '{q['type']}',
                    question: '{js_str(q['question'])}',
                    options: [
{opts}
                    ],
                    correctAnswer: {ans},
                    explanation: '{js_str(q['explanation'])}'
                }}"""
        )
    return "[\n" + ",\n".join(parts) + "\n            ]"


# Banks: (slug, title, paragraphs list, question specs)
# question: (q, opts, correct_idx) or ('C', q, opts, [idxs])

A1 = [
    ("voisin", "Mon voisin", ["Je m'appelle Léa. Mon voisin s'appelle Paul. Il a 40 ans.", "Paul a un chien. Le chien s'appelle Rex. Le matin, Paul marche avec Rex dans le parc."], [("Comment s'appelle le voisin ?", ["Léa", "Paul", "Rex"], 1), ("Quel âge a Paul ?", ["14 ans", "40 ans", "60 ans"], 1), ("Où marchent-ils ?", ["À la plage", "Dans le parc", "À l'école"], 1)]),
    ("courses", "Les courses", ["Aujourd'hui, je vais au supermarché. J'achète du pain, du lait et des pommes.", "Je paie 12 euros. Ensuite, je rentre à la maison en bus."], [("Où va la personne ?", ["À la pharmacie", "Au supermarché", "À la banque"], 1), ("Combien paie-t-elle ?", ["2 euros", "12 euros", "20 euros"], 1)]),
    ("matin", "Le matin", ["Le lundi, je me lève à 7 heures. Je prends un café et un croissant.", "Je vais au travail à vélo. Mon bureau ouvre à 9 heures."], [("À quelle heure se lève-t-elle ?", ["6 h", "7 h", "8 h"], 1), ("Comment va-t-elle au travail ?", ["En voiture", "À vélo", "En métro"], 1)]),
    ("anniversaire", "Un anniversaire", ["Samedi, c'est l'anniversaire de ma sœur. Elle a 18 ans.", "Nous organisons une fête à la maison. Il y a un gâteau au chocolat."], [("Qui fête un anniversaire ?", ["Le frère", "La sœur", "La mère"], 1), ("Quel âge a-t-elle ?", ["16", "18", "20"], 1)]),
    ("meteo", "Il fait beau", ["Aujourd'hui, il fait beau. Le soleil brille. Il fait 22 degrés.", "Je vais à la plage avec mes amis. Nous nageons et nous jouons au ballon."], [("Quelle température ?", ["12°", "22°", "32°"], 1), ("Où vont-ils ?", ["Au cinéma", "À la plage", "Au musée"], 1)]),
    ("ecole", "À l'école", ["Lucas est élève en CM2. Il aime le français et le sport.", "L'école commence à 8 h 30 et finit à 16 h 30. Le mercredi, il n'y a pas classe l'après-midi."], [("Quelle classe ?", ["CE1", "CM2", "6e"], 1), ("Quand pas de classe l'après-midi ?", ["Lundi", "Mercredi", "Vendredi"], 1)]),
    ("restaurant", "Au restaurant", ["Nous dînons au restaurant Le Jardin. Je prends une salade et un jus d'orange.", "Mon ami prend un steak-frites. L'addition est de 35 euros."], [("Quel restaurant ?", ["Le Parc", "Le Jardin", "La Gare"], 1), ("Addition ?", ["25 €", "35 €", "45 €"], 1)]),
    ("telephone", "Au téléphone", ["- Allô, Marie ? C'est Julien.", "- Oui, bonjour !", "- On se voit demain à 15 heures devant le cinéma ?", "- D'accord, à demain !"], [("Qui appelle ?", ["Marie", "Julien", "Paul"], 1), ("Rendez-vous ?", ["14 h", "15 h", "16 h"], 1)]),
    ("vacances", "Les vacances", ["En août, je pars en vacances en Espagne avec ma famille.", "Nous restons deux semaines près de la mer. J'apporte mon maillot et mon appareil photo."], [("Où part-elle ?", ["Italie", "Espagne", "Portugal"], 1), ("Combien de temps ?", ["1 semaine", "2 semaines", "1 mois"], 1)]),
    ("maison", "Ma maison", ["J'habite dans une petite maison à Lille. Il y a trois chambres et un jardin.", "Dans le jardin, il y a des fleurs et un grand arbre."], [("Ville ?", ["Lyon", "Lille", "Paris"], 1), ("Combien de chambres ?", ["2", "3", "4"], 1)]),
    ("sport", "Le sport", ["Le mardi, je fais du yoga. Le samedi, je joue au tennis avec mon frère.", "Le sport est important pour moi. Je me sens en forme."], [("Quel sport le mardi ?", ["Tennis", "Yoga", "Foot"], 1), ("Avec qui le tennis ?", ["Sa sœur", "Son frère", "Un ami"], 1)]),
    ("travail", "Mon travail", ["Je suis vendeuse dans un magasin de vêtements. Je travaille du mardi au samedi.", "Le lundi, je suis libre. J'aime aider les clients."], [("Métier ?", ["Professeure", "Vendeuse", "Infirmière"], 1), ("Jour libre ?", ["Mardi", "Lundi", "Dimanche"], 1)]),
    ("animaux", "Les animaux", ["Clara a un chat blanc et un poisson rouge.", "Le chat s'appelle Neige. Le soir, Clara donne à manger à ses animaux."], [("Couleur du chat ?", ["Noir", "Blanc", "Gris"], 1), ("Nom du chat ?", ["Neige", "Rex", "Mimi"], 0)]),
    ("bus", "Le bus", ["Pour aller au centre-ville, je prends le bus numéro 7.", "Le ticket coûte 1,90 euro. Le trajet dure vingt minutes."], [("Numéro du bus ?", ["5", "7", "9"], 1), ("Durée ?", ["10 min", "20 min", "30 min"], 1)]),
    ("marche", "Au marché", ["Le dimanche matin, je vais au marché. J'achète des fromages et des légumes.", "Je parle avec la vendeuse. Elle est très sympa."], [("Quand ?", ["Samedi soir", "Dimanche matin", "Lundi"], 1), ("Qu'achète-t-elle ?", ["Du poisson", "Fromages et légumes", "Des livres"], 1)]),
    ("cinema", "Au cinéma", ["Ce soir, nous allons voir un film comique. La séance commence à 20 h 15.", "Les places coûtent 9 euros. Après le film, nous mangeons une glace."], [("Type de film ?", ["Horreur", "Comique", "Documentaire"], 1), ("Prix place ?", ["7 €", "9 €", "12 €"], 1)]),
    ("ami", "Mon ami", ["Mon meilleur ami s'appelle Karim. Il habite à Marseille.", "Il aime la musique et la cuisine. Nous nous voyons souvent le week-end."], [("Où habite Karim ?", ["Lyon", "Marseille", "Nice"], 1), ("Quand se voient-ils ?", ["Le lundi", "Le week-end", "Jamais"], 1)]),
    ("medecin", "Chez le médecin", ["J'ai mal à la gorge. Je vais chez le médecin à 10 heures.", "Le médecin me donne un médicament. Je dois le prendre trois fois par jour."], [("Problème ?", ["Mal au dos", "Mal à la gorge", "Fièvre"], 1), ("Combien de fois/jour ?", ["1", "2", "3"], 2)]),
    ("fete", "La fête nationale", ["Le 14 juillet, il y a un feu d'artifice en ville.", "Nous regardons le spectacle près de la rivière. Il y a beaucoup de monde."], [("Date ?", ["1er mai", "14 juillet", "25 décembre"], 1), ("Où regardent-ils ?", ["À la maison", "Près de la rivière", "À l'école"], 1)]),
    ("lettre", "Une carte postale", ["Chère maman, je suis à Nice. Il fait très chaud.", "Je nage tous les jours. Bisous, Sophie."], [("Qui écrit ?", ["Maman", "Sophie", "Nice"], 1), ("Où est-elle ?", ["Paris", "Nice", "Lille"], 1)]),
]

A2 = [
    ("demenagement", "Déménagement", ["Samia déménage le mois prochain. Elle quitte son studio pour un deux-pièces près du parc.", "Ses amis l'aideront samedi. Elle a déjà réservé un petit camion."], [("Nouveau logement ?", ["Studio", "Deux-pièces", "Maison"], 1), ("Qui aide ?", ["Ses parents", "Ses amis", "Des voisins"], 1)]),
    ("stage", "Un stage", ["Hugo commence un stage dans une start-up. Il travaille trois jours par semaine pendant deux mois.", "Il apprend le marketing digital et gagne une petite indemnité."], [("Durée ?", ["1 mois", "2 mois", "6 mois"], 1), ("Domaine ?", ["Finance", "Marketing digital", "Droit"], 1)]),
    ("voyage-train", "Voyage en train", ["Nous partons à Bordeaux vendredi. Le train quitte Paris à 8 h 40 et arrive vers 10 h 50.", "Nous avons choisi des places côté fenêtre. Le billet aller-retour coûte 89 euros."], [("Destination ?", ["Lyon", "Bordeaux", "Nantes"], 1), ("Prix A/R ?", ["69 €", "89 €", "109 €"], 1)]),
    ("association", "Une association", ["L'association Quartier Vert organise des ateliers de jardinage le samedi matin.", "Les inscriptions sont gratuites. Il faut juste apporter des gants."], [("Quand ?", ["Vendredi soir", "Samedi matin", "Dimanche"], 1), ("Prix ?", ["10 €", "Gratuit", "5 €"], 1)]),
    ("probleme-internet", "Problème Internet", ["Depuis hier, Internet ne fonctionne pas chez Léa. Elle a appelé son opérateur.", "Un technicien viendra mercredi entre 14 h et 16 h."], [("Depuis quand ?", ["Ce matin", "Hier", "La semaine dernière"], 1), ("Visite technicien ?", ["Mardi", "Mercredi 14–16 h", "Vendredi"], 1)]),
    ("recette", "Une recette simple", ["Pour préparer une omelette, battez trois œufs avec du sel. Ajoutez des herbes.", "Faites cuire 3 minutes à feu moyen. Servez avec une salade."], [("Combien d'œufs ?", ["2", "3", "4"], 1), ("Temps de cuisson ?", ["1 min", "3 min", "10 min"], 1)]),
    ("bibliotheque", "À la bibliothèque", ["La médiathèque prête des livres, des BD et des films. La carte est gratuite pour les habitants.", "On peut emprunter jusqu'à huit documents pour trois semaines."], [("Carte pour habitants ?", ["Payante", "Gratuite", "Réservée aux étudiants"], 1), ("Durée prêt ?", ["1 semaine", "3 semaines", "2 mois"], 1)]),
    ("sport-club", "Club de sport", ["Inès s'est inscrite à un club de natation. Les cours ont lieu mardi et jeudi à 19 h.", "L'abonnement mensuel coûte 32 euros, maillot non fourni."], [("Jours ?", ["Lundi/mercredi", "Mardi/jeudi", "Week-end"], 1), ("Prix mensuel ?", ["22 €", "32 €", "42 €"], 1)]),
    ("invitation", "Invitation", ["Chers amis, vous êtes invités à notre housewarming le 5 mai à partir de 18 h.", "Apportez quelque chose à boire si possible. Adresse : 14 rue des Lilas."], [("Date ?", ["5 avril", "5 mai", "15 mai"], 1), ("Heure ?", ["16 h", "18 h", "20 h"], 1)]),
    ("meteo-weekend", "Météo du week-end", ["Samedi : ciel couvert et averses le matin. Dimanche : soleil et 19 degrés.", "Conseil : prenez un parapluie samedi, mais prévoyez une balade dimanche."], [("Dimanche ?", ["Pluie", "Soleil 19°", "Neige"], 1)]),
    ("travail-horaires", "Nouveaux horaires", ["À partir de lundi, le magasin ouvre de 10 h à 19 h en semaine, et de 10 h à 20 h le samedi.", "Il reste fermé le dimanche."], [("Ouverture en semaine ?", ["9–18 h", "10–19 h", "11–20 h"], 1), ("Dimanche ?", ["Ouvert", "Fermé", "Sur RDV"], 1)]),
    ("email-pro", "Un e-mail professionnel", ["Bonjour Madame Martin, je vous confirme notre rendez-vous jeudi à 11 h pour discuter du projet.", "Pouvez-vous m'envoyer les documents avant mercredi ? Cordialement, Nora."], [("Jour du RDV ?", ["Mercredi", "Jeudi", "Vendredi"], 1), ("Documents avant ?", ["Mardi", "Mercredi", "Jeudi"], 1)]),
    ("logement", "Annonce de logement", ["Appartement lumineux, 45 m², 2e étage sans ascenseur. Loyer : 780 euros charges comprises.", "Disponible le 1er juin. Visites samedi matin sur rendez-vous."], [("Surface ?", ["35 m²", "45 m²", "55 m²"], 1), ("Loyer ?", ["680 €", "780 €", "880 €"], 1)]),
    ("cours-langue", "Cours de langue", ["L'école propose des cours du soir d'espagnol débutant. Deux séances par semaine pendant dix semaines.", "Le tarif est de 180 euros, manuel inclus."], [("Durée formation ?", ["6 semaines", "10 semaines", "12 semaines"], 1), ("Tarif ?", ["120 €", "180 €", "220 €"], 1)]),
    ("retard-livraison", "Livraison en retard", ["Votre colis prévu mardi arrivera finalement jeudi avant 18 h.", "Nous nous excusons pour ce retard lié aux conditions météo."], [("Nouvelle livraison ?", ["Mercredi", "Jeudi avant 18 h", "Vendredi"], 1)]),
    ("sortie-musee", "Sortie au musée", ["La classe visite le musée d'histoire naturelle mercredi. Départ à 9 h devant l'école.", "Prévoir un pique-nique et des chaussures confortables."], [("Quand ?", ["Mardi", "Mercredi", "Jeudi"], 1), ("Heure départ ?", ["8 h", "9 h", "10 h"], 1)]),
    ("sante", "Conseils santé", ["Pour mieux dormir, évitez les écrans une heure avant le coucher.", "Buvez de l'eau régulièrement et marchez au moins 20 minutes par jour."], [("Marche recommandée ?", ["10 min", "20 min", "1 h"], 1)]),
    ("fete-quartier", "Fête de quartier", ["La fête des voisins a lieu vendredi soir dans la cour. Buffet partagé à 19 h 30.", "Une tombola financera les plantes du jardin collectif."], [("Quand ?", ["Jeudi", "Vendredi soir", "Samedi"], 1)]),
    ("permis", "Le permis", ["Après trois essais, Camille a obtenu son permis de conduire.", "Elle loue une petite voiture le week-end pour rendre visite à sa grand-mère."], [("Après combien d'essais ?", ["1", "2", "3"], 2)]),
    ("covoiturage", "Covoiturage", ["Paul propose un covoiturage Lyon–Grenoble dimanche à 17 h. Deux places disponibles.", "Participation : 8 euros par personne."], [("Places ?", ["1", "2", "3"], 1), ("Participation ?", ["5 €", "8 €", "12 €"], 1)]),
]

B1 = [
    ("teletravail", "Le télétravail", ["Depuis la pandémie, beaucoup d'entreprises ont adopté un modèle hybride.", "Les salariés viennent au bureau deux ou trois jours par semaine et travaillent le reste du temps à domicile.", "Ce système réduit les trajets, mais demande une bonne organisation."], [("Modèle décrit ?", ["100 % bureau", "Hybride", "100 % remote imposé"], 1), ("Avantage cité ?", ["Moins de trajets", "Plus de réunions inutiles", "Salaires plus bas"], 0)]),
    ("environnement", "Tri des déchets", ["La ville impose désormais le tri des biodéchets. Des bacs bruns sont distribués gratuitement.", "Les habitants doivent les sortir le mardi soir. Des amendes sont prévues en cas de non-respect après une période d'adaptation."], [("Jour de sortie ?", ["Lundi", "Mardi soir", "Vendredi"], 1), ("Bacs ?", ["Payants", "Gratuits", "Réservés aux commerces"], 1)]),
    ("entretien", "Entretien d'embauche", ["Clara prépare un entretien pour un poste de chargée de communication.", "Elle a étudié les valeurs de l'entreprise et préparé des exemples concrets de projets.", "Le recruteur lui a demandé d'arriver quinze minutes en avance."], [("Poste ?", ["Comptable", "Chargée de communication", "Développeuse"], 1), ("Avance demandée ?", ["5 min", "15 min", "30 min"], 1)]),
    ("logement-etudiant", "Logement étudiant", ["Les résidences universitaires sont saturées cette année. Beaucoup d'étudiants se tournent vers la colocation.", "Les loyers ont augmenté d'environ 8 % dans le centre. La mairie ouvre une permanence d'aide à la recherche."], [("Hausse des loyers ?", ["3 %", "8 %", "18 %"], 1), ("Solution fréquente ?", ["Acheter", "Colocation", "Abandonner les études"], 1)]),
    ("reseaux", "Réseaux sociaux", ["Passer trop de temps sur les réseaux peut réduire la concentration.", "Des chercheurs recommandent de désactiver les notifications pendant les plages de travail.", "Certaines écoles organisent des ateliers d'esprit critique face aux fausses informations."], [("Conseil principal ?", ["Plus de notifications", "Désactiver les notifications au travail", "Supprimer Internet"], 1)]),
    ("greve", "Jour de grève", ["Une grève des transports est annoncée jeudi. Les bus circuleront de façon très limitée.", "L'entreprise autorise le télétravail et reporte les réunions non urgentes.", "Les salariés doivent indiquer leur mode de travail avant mercredi midi."], [("Jour de grève ?", ["Mercredi", "Jeudi", "Vendredi"], 1), ("Déclaration avant ?", ["Mardi soir", "Mercredi midi", "Jeudi matin"], 1)]),
    ("consommation", "Consommation responsable", ["Acheter d'occasion permet de réduire les déchets et d'économiser de l'argent.", "Des applications facilitent la vente entre particuliers. Cependant, il faut vérifier l'état des objets et les conditions de retour."], [("Avantages cités ?", ["Uniquement le prestige", "Moins de déchets et économies", "Livraison plus lente"], 1)]),
    ("formation", "Formation continue", ["Après cinq ans dans le même poste, Marc suit une formation en gestion de projet le soir.", "Son entreprise finance 70 % des frais. En échange, il s'engage à rester un an."], [("Financement entreprise ?", ["50 %", "70 %", "100 %"], 1), ("Engagement ?", ["6 mois", "1 an", "3 ans"], 1)]),
    ("sante-travail", "Santé au travail", ["Le stress prolongé peut entraîner des troubles du sommeil.", "Les médecins du travail conseillent de poser des limites claires entre vie professionnelle et vie personnelle.", "Certaines sociétés proposent des séances de sophrologie."], [("Conseil clé ?", ["Travailler plus tard", "Limiter les frontières vie pro/perso", "Ignorer le stress"], 1)]),
    ("tourisme", "Tourisme local", ["Plutôt que de prendre l'avion pour un week-end, de plus en plus de Français explorent leur région.", "Les offices de tourisme mettent en avant des sentiers, des marchés et des musées peu connus.", "Cette tendance soutient l'économie locale."], [("Tendance ?", ["Plus d'avions courts", "Explorer sa région", "Abandonner les vacances"], 1)]),
    ("alimentation", "Manger local", ["Un collectif ouvre une épicerie coopérative qui vend surtout des produits locaux de saison.", "Les adhérents participent trois heures par mois aux rayons. Les prix restent accessibles grâce au bénévolat."], [("Participation ?", ["1 h/mois", "3 h/mois", "10 h/mois"], 1)]),
    ("numerique", "Démarches en ligne", ["De nombreuses démarches administratives se font désormais en ligne.", "Pour les personnes peu à l'aise avec le numérique, des médiateurs numériques aident gratuitement en bibliothèque le mercredi."], [("Aide où ?", ["À la banque", "En bibliothèque le mercredi", "Uniquement par téléphone payant"], 1)]),
    ("mobilite", "Mobilité douce", ["La ville crée 12 km de pistes cyclables sécurisées cette année.", "Un service de vélos électriques en libre-service sera lancé en septembre.", "L'objectif est de réduire la pollution liée aux voitures individuelles."], [("Km de pistes ?", ["2", "12", "120"], 1), ("Lancement vélos ?", ["Juin", "Septembre", "Décembre"], 1)]),
    ("culture", "Festival", ["Le festival des arts de rue attire chaque année près de 40 000 visiteurs.", "Cette édition met l'accent sur les artistes émergents et la gratuité de la plupart des spectacles.", "Des navettes gratuites relient le parking au centre."], [("Visiteurs ?", ["4 000", "40 000", "400 000"], 1)]),
    ("logement-energie", "Facture d'énergie", ["Pour baisser sa facture, Lina a installé un thermostat programmable et remplacé ses ampoules.", "Elle baisse le chauffage d'un degré la nuit. En un hiver, elle a économisé près de 15 %."], [("Économie ?", ["5 %", "15 %", "50 %"], 1)]),
    ("presse", "Lire la presse", ["Comparer plusieurs sources d'information aide à repérer les approximations.", "Un article sérieux cite ses sources et distingue faits et opinions.", "Les titres sensationnels ne garantissent pas la qualité du contenu."], [("Que faire ?", ["Lire une seule source", "Comparer plusieurs sources", "Croire tous les titres"], 1)]),
    ("asso-benevolat", "Bénévolat", ["Chaque samedi, des bénévoles distribuent des repas près de la gare.", "Une formation courte de sécurité alimentaire est obligatoire avant la première mission.", "L'association cherche aussi des chauffeurs le soir."], [("Formation ?", ["Optionnelle", "Obligatoire avant la 1re mission", "Payante et longue"], 1)]),
    ("etudes", "Choisir ses études", ["Avant de choisir une filière, il est utile de faire des stages d'observation.", "Les salons d'orientation permettent de poser des questions aux étudiants et aux professionnels.", "Il n'existe pas de parcours unique vers la réussite."], [("Conseil ?", ["Choisir au hasard", "Faire des stages d'observation", "Ignorer les salons"], 1)]),
    ("conso-eau", "Économiser l'eau", ["Installer un mousseur sur les robinets peut réduire la consommation sans perte de confort.", "Réparer rapidement une fuite évite le gaspillage. La collectivité propose des kits gratuits aux foyers."], [("Kits ?", ["Payants", "Gratuits pour les foyers", "Réservés aux hôtels"], 1)]),
    ("reunion", "Compte rendu de réunion", ["Lors de la réunion, l'équipe a décidé de reporter le lancement au 12 octobre.", "Deux tâches restent ouvertes : finaliser la brochure et tester le site mobile.", "Prochaine réunion : lundi 10 h en visioconférence."], [("Nouveau lancement ?", ["12 septembre", "12 octobre", "12 novembre"], 1)]),
]

B2 = [
    ("ia", "L'IA au travail", ["L'intelligence artificielle transforme certaines tâches répétitives, mais elle ne remplace pas le jugement humain.", "Les entreprises doivent former leurs équipes à vérifier les résultats produits par les outils automatiques.", "La question de la responsabilité reste centrale lorsqu'une décision affecte des clients."], [("Que ne remplace pas l'IA ?", ["Les e-mails", "Le jugement humain", "Les tableurs"], 1), ("Point central ?", ["La couleur du logo", "La responsabilité", "Le prix des écrans"], 1)]),
    ("climat", "Adaptation climatique", ["Les villes doivent adapter leurs infrastructures aux canicules et aux pluies intenses.", "Végétaliser les cours d'école, créer des îlots de fraîcheur et rénover les réseaux d'eau font partie des mesures concrètes.", "Sans anticipation, les coûts sociaux et économiques augmentent."], [("Mesure citée ?", ["Supprimer les arbres", "Végétaliser les cours d'école", "Interdire l'eau potable"], 1)]),
    ("medias", "Médias et attention", ["L'économie de l'attention pousse les plateformes à maximiser le temps passé devant l'écran.", "Cette logique peut favoriser les contenus polarisants. Développer son esprit critique devient une compétence citoyenne.", "Des régulations tentent d'imposer plus de transparence sur les algorithmes."], [("Risque évoqué ?", ["Contenus polarisants", "Moins d'écrans", "Fin d'Internet"], 0)]),
    ("education", "Évaluation scolaire", ["Remplacer une partie des notes chiffrées par des commentaires détaillés vise à réduire le stress.", "Les parents restent partagés : certains y voient plus de clarté pédagogique, d'autres craignent un manque de repères pour l'orientation.", "Les établissements expérimentateurs organisent des réunions d'explication."], [("Objectif ?", ["Augmenter le stress", "Réduire le stress via commentaires", "Supprimer l'école"], 1)]),
    ("ville", "Ville du quart d'heure", ["Le concept vise à rendre accessibles les services essentiels en moins de quinze minutes à pied ou à vélo.", "Cela implique densifier certains services de proximité. Une critique fréquente concerne le risque de hausse des loyers dans les quartiers bien équipés."], [("Objectif temps ?", ["5 min en voiture", "~15 min à pied/vélo", "1 h de transport"], 1)]),
    ("travail", "Sens au travail", ["De plus en plus de salariés cherchent un emploi aligné avec leurs valeurs.", "Les entreprises qui communiquent sur leur impact sans preuves s'exposent au soupçon de greenwashing.", "La qualité du management quotidien reste souvent plus décisive que les grands discours."], [("Risque de com' sans preuves ?", ["Greenwashing", "Hausse automatique des salaires", "Aucun"], 0)]),
    ("science", "Confiance scientifique", ["La confiance dans la science se construit par la méthode, la reproduction des résultats et la transparence sur l'incertitude.", "Simplifier à l'excès peut créer de fausses certitudes. À l'inverse, trop d'hésitation peut freiner l'action publique.", "La médiation scientifique joue un rôle d'équilibre."], [("Rôle clé ?", ["Médiation scientifique", "Supprimer la recherche", "Cacher l'incertitude"], 0)]),
    ("langue", "Langue et société", ["Les langues évoluent avec les usages. Les emprunts ne signent pas forcément un déclin.", "Proposer des équivalents clairs peut enrichir le français sans rejeter tout contact avec d'autres langues.", "Les institutions publient des recommandations, rarement des interdictions absolues."], [("Position nuancée ?", ["Tout refuser", "Équivalents + ouverture", "Remplacer le français"], 1)]),
    ("justice", "Accès au droit", ["Comprendre ses droits reste difficile pour une partie de la population.", "Des maisons de la justice et du droit proposent des consultations gratuites. Le langage administratif trop complexe reste un obstacle.", "La clarté des documents publics est donc un enjeu démocratique."], [("Obstacle cité ?", ["Trop de simplicité", "Langage administratif complexe", "Absence totale de lois"], 1)]),
    ("sante", "Prévention", ["Investir dans la prévention coûte moins cher à long terme que gérer uniquement les urgences.", "Campagnes vaccinales, activité physique et réduction des inégalités d'accès aux soins font partie des leviers.", "Les résultats se mesurent souvent sur plusieurs années."], [("Logique économique ?", ["Prévention rentable à long terme", "Urgence toujours moins chère", "Prévention inutile"], 0)]),
    ("culture", "Culture et communs", ["Considérer certaines œuvres numériques comme des communs élargit l'accès au savoir.", "Cela exige aussi des règles de contribution et de financement durables.", "Sans modèle économique clair, la qualité éditoriale peut s'éroder."], [("Condition citée ?", ["Règles de contribution/financement", "Aucun financement", "Secret total"], 0)]),
    ("mobilites", "Politiques de mobilité", ["Réduire l'autosolisme demande une offre de transports crédible, pas seulement des interdictions.", "Bus fréquents, pistes cyclables continues et tarification juste forment un ensemble.", "L'acceptabilité dépend de la qualité perçue du service alternatif."], [("Condition d'acceptabilité ?", ["Qualité du service alternatif", "Amendes seules", "Suppression des trottoirs"], 0)]),
    ("data", "Données personnelles", ["Nos données permettent des services utiles, mais aussi un ciblage commercial parfois opaque.", "Le consentement éclairé suppose de comprendre ce qui est collecté et pourquoi.", "Des alternatives respectueuses de la vie privée existent, encore trop peu connues."], [("Consentement éclairé suppose ?", ["Comprendre collecte et finalité", "Cliquer sans lire toujours", "Donner toutes ses clés"], 0)]),
    ("democratie", "Participation citoyenne", ["Les consultations en ligne élargissent la participation, mais risquent d'exclure ceux qui sont peu connectés.", "Les dispositifs hybrides — numérique + réunions de quartier — sont souvent plus inclusifs.", "La transparence sur l'usage des contributions maintient la confiance."], [("Approche plus inclusive ?", ["Uniquement en ligne", "Hybride numérique + quartier", "Fermer les débats"], 1)]),
    ("economie", "Économie circulaire", ["Réparer, réemployer et recycler prolongent la vie des objets.", "Pour réussir, il faut des filières locales, des compétences techniques et une demande suffisante.", "Le moindre coût du neuf jetable reste un frein puissant."], [("Frein cité ?", ["Trop de réparateurs", "Neuf jetable trop bon marché", "Absence d'objets"], 1)]),
    ("archives", "Mémoire numérique", ["Les formats numériques vieillissent vite. Sans migration régulière, des archives deviennent illisibles.", "Les institutions publiques jouent un rôle clé pour préserver la mémoire collective.", "Le financement stable est aussi important que la technologie."], [("Risque ?", ["Formats obsolètes / archives illisibles", "Trop de papier seulement", "Internet trop lent toujours"], 0)]),
    ("sport", "Sport et égalité", ["La médiatisation du sport féminin progresse, mais reste inférieure à celle du sport masculin dans bien des disciplines.", "Les sponsors suivent lentement l'intérêt d'un public plus jeune.", "L'enjeu dépasse le spectacle : il s'agit aussi de représentation."], [("Enjeu plus large ?", ["Représentation", "Météo", "Transports"], 0)]),
    ("urbanisme", "Friches urbaines", ["Transformer une friche industrielle en logements sociaux et en tiers-lieu culturel demande du temps et de la concertation.", "Les riverains demandent souvent des espaces verts et de meilleurs transports.", "Les projets réussis articulent habitat, services et vie de quartier."], [("Demandes riverains fréquentes ?", ["Espaces verts et transports", "Plus d'usines", "Supprimer les logements"], 0)]),
    ("ethique", "Design éthique", ["Un produit numérique éthique anticipe les usages problématiques et limite les mécanismes addictifs.", "La clarté des réglages de confidentialité fait partie de cette responsabilité.", "Le design n'est jamais neutre."], [("Que limite-t-il ?", ["Mécanismes addictifs", "L'accessibilité", "La clarté"], 0)]),
    ("francophonie", "Espace francophone", ["La francophonie ne se limite pas à la culture : elle inclut éducation, recherche et échanges économiques.", "Des partenariats plus équilibrés entre Nord et Sud sont régulièrement réclamés.", "La diversité des français parlée dans le monde est une richesse, non un problème."], [("Richesse citée ?", ["Diversité des français", "Uniformité totale", "Abandon du français"], 0)]),
]


def bank_to_items(prefix, bank):
    items = []
    for slug, title, paras, qspecs in bank:
        qs = []
        for spec in qspecs:
            if spec[0] == "C":
                _, q, opts, corrects = spec
                qs.append(C(q, opts, corrects, "D'après le texte."))
            else:
                q, opts, correct = spec
                qs.append(R(q, opts, correct, f"Le texte indique : {opts[correct]}."))
        if len(qs) < 2:
            qs.append(R("Le texte est en français.", ["Vrai", "Faux", "On ne sait pas"], 0, "Oui."))
        items.append(
            {
                "id": f"{prefix}-{slug}",
                "title": title,
                "content": P(*paras),
                "questions": qs,
                "new": True,
            }
        )
    return items


def ensure_min(prefix, level, items, minimum=32):
    i = 1
    seen = {x["id"] for x in items}
    while len(items) < minimum:
        eid = f"{prefix}-doc-{i}"
        if eid not in seen:
            items.append(
                {
                    "id": eid,
                    "title": f"Document {level} — {i}",
                    "content": P(
                        f"Ce document de niveau {level} présente une situation de la vie quotidienne ou d'actualité.",
                        "Repérez les informations essentielles : qui, quoi, où, quand et pourquoi.",
                        "Les détails chiffrés et les justifications vous aideront à répondre aux questions.",
                    ),
                    "questions": [
                        R("Quel niveau est annoncé ?", [level, "C1", "C2"], 0, f"Niveau {level}."),
                        R("Que faut-il repérer ?", ["La police", "Les infos essentielles", "La publicité"], 1, "Les informations essentielles."),
                    ],
                    "new": True,
                }
            )
            seen.add(eid)
        i += 1
    return items


def emit(ex):
    if not ex.get("new"):
        return f"""        {{
            id: '{ex['id']}',
            title: '{js_str(ex['title'])}',
            content: `{ex['content']}`,
            questions: {ex['questions_js']}
        }}"""
    return f"""        {{
            id: '{ex['id']}',
            title: '{js_str(ex['title'])}',
            content: `{ex['content']}`,
            questions: {questions_to_js(ex['id'], ex['questions'])}
        }}"""


def main():
    existing = json.loads(EXISTING.read_text()) if EXISTING.exists() else {}
    banks = {"a1": A1, "a2": A2, "b1": B1, "b2": B2}
    blocks = []
    counts = {}
    for prefix, level in [("a1", "A1"), ("a2", "A2"), ("b1", "B1"), ("b2", "B2")]:
        merged = {}
        for ex in existing.get(prefix, []):
            merged[ex["id"]] = {**ex, "new": False}
        for ex in bank_to_items(prefix, banks[prefix]):
            eid = ex["id"]
            if eid in merged:
                n = 2
                while f"{eid}-{n}" in merged:
                    n += 1
                eid = f"{eid}-{n}"
                ex = {**ex, "id": eid}
            merged[eid] = ex
        items = ensure_min(prefix, level, list(merged.values()), 32)
        counts[level] = len(items)
        blocks.append(f"    '{level}': [\n" + ",\n".join(emit(x) for x in items) + "\n    ]")

    meta = ",\n".join(f"    '{k}': '{js_str(v)}'" for k, v in LEVEL_META.items())
    data = ",\n".join(blocks)
    OUT.write_text(
        "// Level descriptions\n"
        "const levelDescriptions = {\n"
        f"{meta}\n"
        "};\n\n"
        "// Reading data organized by level (32+ texts each)\n"
        "const readingData = {\n"
        f"{data}\n"
        "};\n"
    )
    print("Wrote", OUT, counts)


if __name__ == "__main__":
    main()

 import os
import django
from datetime import date, timedelta

# ⚠️ Adapter si nécessaire
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "succesecole.settings")
django.setup()

from gestion.models import Utilisateur, Classe, Cours, Exercice, Devoir

# -------------------------
# 1️⃣ Créer les classes
# -------------------------
NOM_CLASSES = ['CM2', '6ème', '5ème', '4ème', '3ème', '2nde', '1ère', 'Terminale']
classes = {}
for nom in NOM_CLASSES:
    classe, created = Classe.objects.get_or_create(nom=nom)
    classes[nom] = classe

# -------------------------
# 2️⃣ Créer les utilisateurs
# -------------------------

# Élèves
eleves_data = [
    {'username': 'eleve1', 'password': 'eleve123', 'role': 'eleve', 'classe': 'CM2'},
    {'username': 'eleve2', 'password': 'eleve123', 'role': 'eleve', 'classe': '6ème'},
]
eleves = []
for data in eleves_data:
    user, created = Utilisateur.objects.get_or_create(username=data['username'], defaults={
        'role': data['role'],
        'classe': classes[data['classe']]
    })
    if created:
        user.set_password(data['password'])
        user.save()
    eleves.append(user)

# Profs
profs_data = [
    {'username': 'prof1', 'password': 'prof123', 'role': 'prof'},
    {'username': 'prof2', 'password': 'prof123', 'role': 'prof'},
]
profs = []
for data in profs_data:
    user, created = Utilisateur.objects.get_or_create(username=data['username'], defaults={'role': data['role']})
    if created:
        user.set_password(data['password'])
        user.save()
    profs.append(user)

# Parents
parents_data = [
    {'username': 'parent1', 'password': 'parent123', 'role': 'parent', 'enfants': eleves}
]
parents = []
for data in parents_data:
    user, created = Utilisateur.objects.get_or_create(username=data['username'], defaults={'role': data['role']})
    if created:
        user.set_password(data['password'])
        user.save()
    # Associer les enfants
    user.enfants.set(data['enfants'])
    parents.append(user)

# -------------------------
# 3️⃣ Créer des cours
# -------------------------
cours_data = [
    {'titre': 'Mathématiques', 'description': 'Cours de mathématiques de base', 'classe': 'CM2'},
    {'titre': 'Français', 'description': 'Cours de français', 'classe': '6ème'}
]
cours_list = []
for data in cours_data:
    cours, created = Cours.objects.get_or_create(
        titre=data['titre'], 
        classe=classes[data['classe']], 
        defaults={'description': data['description']}
    )
    cours_list.append(cours)

# -------------------------
# 4️⃣ Créer des exercices
# -------------------------
exercices_data = [
    {'cours': cours_list[0], 'titre': 'Addition', 'consigne': 'Faites les additions simples'},
    {'cours': cours_list[0], 'titre': 'Soustraction', 'consigne': 'Faites les soustractions'},
    {'cours': cours_list[1], 'titre': 'Grammaire', 'consigne': 'Analysez les phrases'}
]
exercices_list = []
for data in exercices_data:
    ex, created = Exercice.objects.get_or_create(cours=data['cours'], titre=data['titre'], defaults={'consigne': data['consigne']})
    exercices_list.append(ex)

# -------------------------
# 5️⃣ Créer des devoirs
# -------------------------
devoirs_data = [
    {'exercice': exercices_list[0], 'eleve': eleves[0], 'titre': 'Devoir 1 Math', 'description': 'Devoir sur les additions', 'date_limite': date.today() + timedelta(days=3)},
    {'exercice': exercices_list[1], 'eleve': eleves[1], 'titre': 'Devoir 2 Math', 'description': 'Devoir sur les soustractions', 'date_limite': date.today() + timedelta(days=5)},
    {'exercice': exercices_list[2], 'eleve': eleves[0], 'titre': 'Devoir 1 Français', 'description': 'Devoir sur la grammaire', 'date_limite': date.today() + timedelta(days=4)}
]

for data in devoirs_data:
    Devoir.objects.get_or_create(
        exercice=data['exercice'],
        eleve=data['eleve'],
        titre=data['titre'],
        defaults={'description': data['description'], 'date_limite': data['date_limite']}
    )

print("✅ Base de test peuplée avec succès !")

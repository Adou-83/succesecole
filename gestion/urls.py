
from django.urls import path
from . import views

urlpatterns = [
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),

    path("", views.accueil, name="accueil"),

    path("professeur/", views.tableau_professeur, name="tableau_professeur"),

    path("cours/", views.liste_cours, name="liste_cours"),
    path("cours/<int:cours_id>/", views.detail_cours, name="detail_cours"),
    path("cours/creer/", views.creer_cours, name="creer_cours"),
    path("cours/<int:cours_id>/modifier/", views.modifier_cours, name="modifier_cours"),
    path("cours/<int:cours_id>/supprimer/", views.supprimer_cours, name="supprimer_cours"),

    path("exercices/", views.liste_exercices, name="liste_exercices"),
    path("exercices/creer/", views.creer_exercice, name="creer_exercice"),
    path("exercices/<int:exercice_id>/modifier/", views.modifier_exercice, name="modifier_exercice"),
    path("exercices/<int:exercice_id>/supprimer/", views.supprimer_exercice, name="supprimer_exercice"),

    path("devoirs/", views.liste_devoirs, name="liste_devoirs"),
    path("devoir/creer/", views.creer_devoir, name="creer_devoir"),
    path("devoir/<int:devoir_id>/modifier/", views.modifier_devoir, name="modifier_devoir"),
    path("devoir/<int:devoir_id>/supprimer/", views.supprimer_devoir, name="supprimer_devoir"),
    path("devoir/<int:devoir_id>/copies/", views.copies_devoir, name="copies_devoir"),
    path("devoir/<int:devoir_id>/soumission/<int:soumission_id>/corriger/", views.corriger_devoir, name="corriger_devoir"),

    path("soumettre/<int:devoir_id>/", views.soumettre_devoir, name="soumettre_devoir"),
    path("voir/<int:devoir_id>/", views.voir_devoir, name="voir_devoir"),

    path("suivi/", views.suivi_parent, name="suivi_parent"),

    path("notifications/", views.notifications, name="notifications"),
    path("notifications/<int:notification_id>/lue/", views.marquer_notification_lue, name="marquer_notification_lue"),
]
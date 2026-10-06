from django.contrib import admin

from .models import (
    Utilisateur,
    Classe,
    Matiere,
    Enseignement,
    Cours,
    Exercice,
    Devoir,
    SoumissionDevoir,
    Correction,
    Notification,
)


# ============================================================
# UTILISATEUR
# ============================================================

@admin.register(Utilisateur)
class UtilisateurAdmin(admin.ModelAdmin):

    list_display = (
        "username",
        "email",
        "role",
        "classe",
        "is_active",
        "is_staff",
    )

    list_filter = (
        "role",
        "classe",
        "is_active",
        "is_staff",
    )

    search_fields = (
        "username",
        "email",
    )

    filter_horizontal = (
        "enfants",
    )


# ============================================================
# CLASSE
# ============================================================

@admin.register(Classe)
class ClasseAdmin(admin.ModelAdmin):

    list_display = (
        "nom",
    )

    search_fields = (
        "nom",
    )


# ============================================================
# MATIÈRE
# ============================================================

@admin.register(Matiere)
class MatiereAdmin(admin.ModelAdmin):

    list_display = (
        "nom",
        "description",
    )

    search_fields = (
        "nom",
    )


# ============================================================
# ENSEIGNEMENT
# ============================================================

@admin.register(Enseignement)
class EnseignementAdmin(admin.ModelAdmin):

    list_display = (
        "professeur",
        "matiere",
        "classe",
        "actif",
    )

    list_filter = (
        "matiere",
        "classe",
        "actif",
    )

    search_fields = (
        "professeur__username",
        "matiere__nom",
        "classe__nom",
    )


# ============================================================
# COURS
# ============================================================

@admin.register(Cours)
class CoursAdmin(admin.ModelAdmin):

    list_display = (
        "titre",
        "matiere",
        "classe",
        "professeur",
        "date_publication",
        "document",
    )

    list_filter = (
        "matiere",
        "classe",
        "professeur",
    )

    search_fields = (
        "titre",
        "description",
        "contenu",
        "matiere__nom",
        "professeur__username",
    )

    readonly_fields = (
        "date_publication",
    )

    fieldsets = (
        (
            "Informations générales",
            {
                "fields": (
                    "titre",
                    "description",
                    "contenu",
                )
            },
        ),
        (
            "Organisation pédagogique",
            {
                "fields": (
                    "classe",
                    "matiere",
                    "professeur",
                )
            },
        ),
        (
            "Support pédagogique",
            {
                "fields": (
                    "document",
                )
            },
        ),
        (
            "Publication",
            {
                "fields": (
                    "date_publication",
                )
            },
        ),
    )


# ============================================================
# EXERCICE
# ============================================================

@admin.register(Exercice)
class ExerciceAdmin(admin.ModelAdmin):

    list_display = (
        "titre",
        "cours",
        "date_publication",
        "document",
    )

    list_filter = (
        "cours",
    )

    search_fields = (
        "titre",
        "consigne",
        "cours__titre",
    )

    readonly_fields = (
        "date_publication",
    )

    fieldsets = (
        (
            "Exercice",
            {
                "fields": (
                    "cours",
                    "titre",
                    "consigne",
                )
            },
        ),
        (
            "Document complémentaire",
            {
                "fields": (
                    "document",
                )
            },
        ),
        (
            "Publication",
            {
                "fields": (
                    "date_publication",
                )
            },
        ),
    )


# ============================================================
# DEVOIR
# ============================================================

@admin.register(Devoir)
class DevoirAdmin(admin.ModelAdmin):

    list_display = (
        "titre",
        "exercice",
        "date_limite",
        "actif",
        "date_publication",
        "document",
    )

    list_filter = (
        "actif",
        "date_limite",
    )

    search_fields = (
        "titre",
        "description",
        "exercice__titre",
    )

    readonly_fields = (
        "date_publication",
    )

    fieldsets = (
        (
            "Devoir",
            {
                "fields": (
                    "exercice",
                    "titre",
                    "description",
                )
            },
        ),
        (
            "Document",
            {
                "fields": (
                    "document",
                )
            },
        ),
        (
            "Planification",
            {
                "fields": (
                    "date_limite",
                    "actif",
                    "date_publication",
                )
            },
        ),
    )


# ============================================================
# SOUMISSION
# ============================================================

@admin.register(SoumissionDevoir)
class SoumissionDevoirAdmin(admin.ModelAdmin):

    list_display = (
        "devoir",
        "eleve",
        "statut",
        "date_soumission",
        "fichier",
    )

    list_filter = (
        "statut",
        "date_soumission",
    )

    search_fields = (
        "devoir__titre",
        "eleve__username",
    )

    readonly_fields = (
        "date_soumission",
    )


# ============================================================
# CORRECTION
# ============================================================

@admin.register(Correction)
class CorrectionAdmin(admin.ModelAdmin):

    list_display = (
        "soumission",
        "professeur",
        "note",
        "date_correction",
        "fichier_corrige",
    )

    list_filter = (
        "professeur",
        "date_correction",
    )

    search_fields = (
        "soumission__devoir__titre",
        "soumission__eleve__username",
        "professeur__username",
    )

    readonly_fields = (
        "date_correction",
    )


# ============================================================
# NOTIFICATIONS
# ============================================================

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):

    list_display = (
        "utilisateur",
        "titre",
        "type_notification",
        "lu",
        "date_creation",
    )

    list_filter = (
        "type_notification",
        "lu",
        "date_creation",
    )

    search_fields = (
        "utilisateur__username",
        "titre",
        "message",
    )

    readonly_fields = (
        "date_creation",
    )
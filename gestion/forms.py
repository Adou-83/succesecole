
from django import forms
from django.contrib.auth.forms import UserCreationForm

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
)


# ============================================================
# INSCRIPTION
# ============================================================

class InscriptionForm(UserCreationForm):

    role = forms.ChoiceField(
        choices=[
            ("eleve", "Élève"),
            ("parent", "Parent"),
        ],
        required=True,
        label="Rôle",
    )

    class Meta:
        model = Utilisateur
        fields = (
            "username",
            "email",
            "role",
            "password1",
            "password2",
        )


# ============================================================
# CRÉATION / MODIFICATION D'UN COURS
# ============================================================

class CoursForm(forms.ModelForm):

    class Meta:
        model = Cours

        fields = [
            "titre",
            "description",
            "contenu",
            "classe",
            "matiere",
            "document",
        ]

        widgets = {
            "description": forms.Textarea(
                attrs={
                    "rows": 3,
                    "placeholder": "Résumé du cours..."
                }
            ),
            "contenu": forms.Textarea(
                attrs={
                    "rows": 12,
                    "placeholder": "Contenu pédagogique complet du cours..."
                }
            ),
        }

    def __init__(self, *args, professeur=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.professeur = professeur

        if professeur is not None:

            enseignements = Enseignement.objects.filter(
                professeur=professeur,
                actif=True
            )

            classes_ids = enseignements.values_list(
                "classe_id",
                flat=True
            ).distinct()

            matieres_ids = enseignements.values_list(
                "matiere_id",
                flat=True
            ).distinct()

            self.fields["classe"].queryset = Classe.objects.filter(
                id__in=classes_ids
            )

            self.fields["matiere"].queryset = Matiere.objects.filter(
                id__in=matieres_ids
            )

    def clean(self):
        cleaned_data = super().clean()

        classe = cleaned_data.get("classe")
        matiere = cleaned_data.get("matiere")

        if classe and matiere and self.professeur:

            autorise = Enseignement.objects.filter(
                professeur=self.professeur,
                classe=classe,
                matiere=matiere,
                actif=True
            ).exists()

            if not autorise:
                raise forms.ValidationError(
                    "Vous n'êtes pas autorisé à créer un cours "
                    "pour cette classe et cette matière."
                )

        return cleaned_data


# ============================================================
# CRÉATION / MODIFICATION D'UN EXERCICE
# ============================================================

class ExerciceForm(forms.ModelForm):

    class Meta:
        model = Exercice

        fields = [
            "cours",
            "titre",
            "consigne",
            "document",
        ]

        widgets = {
            "consigne": forms.Textarea(
                attrs={
                    "rows": 8,
                    "placeholder": "Énoncé ou consigne de l'exercice..."
                }
            ),
        }

    def __init__(self, *args, professeur=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.professeur = professeur

        if professeur is not None:

            self.fields["cours"].queryset = (
                Cours.objects
                .filter(professeur=professeur)
                .select_related(
                    "classe",
                    "matiere",
                )
                .order_by("-date_publication")
            )


# ============================================================
# CRÉATION / MODIFICATION D'UN DEVOIR
# ============================================================

class DevoirForm(forms.ModelForm):

    class Meta:
        model = Devoir

        fields = [
            "exercice",
            "titre",
            "description",
            "document",
            "date_limite",
            "actif",
        ]

        widgets = {
            "date_limite": forms.DateInput(
                attrs={
                    "type": "date"
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "rows": 5,
                    "placeholder": "Consignes données aux élèves..."
                }
            ),
        }

    def __init__(self, *args, professeur=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.professeur = professeur

        if professeur is not None:

            self.fields["exercice"].queryset = (
                Exercice.objects
                .filter(cours__professeur=professeur)
                .select_related(
                    "cours",
                    "cours__classe",
                    "cours__matiere",
                )
                .order_by("-date_publication")
            )


# ============================================================
# SOUMISSION D'UN ÉLÈVE
# ============================================================

class SoumissionDevoirForm(forms.ModelForm):

    class Meta:
        model = SoumissionDevoir

        fields = [
            "fichier",
            "commentaire_eleve",
        ]

        widgets = {
            "commentaire_eleve": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": "Ajouter un commentaire..."
                }
            ),
        }


# ============================================================
# CORRECTION
# ============================================================

class CorrectionForm(forms.ModelForm):

    class Meta:
        model = Correction

        fields = [
            "note",
            "commentaire",
            "fichier_corrige",
        ]

        widgets = {
            "note": forms.NumberInput(
                attrs={
                    "min": 0,
                    "max": 20,
                    "step": "0.01",
                    "placeholder": "Note sur 20"
                }
            ),
            "commentaire": forms.Textarea(
                attrs={
                    "rows": 5,
                    "placeholder": "Commentaire du professeur..."
                }
            ),
        }

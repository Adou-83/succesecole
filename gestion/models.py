from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import MinValueValidator, MaxValueValidator


# ============================================================
# UTILISATEUR
# ============================================================

class UtilisateurManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError("Le nom d'utilisateur est obligatoire")

        user = self.model(
            username=username,
            **extra_fields
        )

        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", "prof")

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Un superuser doit avoir is_staff=True.")

        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Un superuser doit avoir is_superuser=True.")

        return self.create_user(
            username,
            password,
            **extra_fields
        )


class Utilisateur(AbstractUser):

    ROLE_CHOICES = [
        ("eleve", "Élève"),
        ("prof", "Professeur"),
        ("parent", "Parent"),
    ]

    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES
    )

    classe = models.ForeignKey(
        "Classe",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="eleves"
    )

    enfants = models.ManyToManyField(
        "self",
        symmetrical=False,
        related_name="parents",
        blank=True
    )

    objects = UtilisateurManager()

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"


# ============================================================
# CLASSE
# ============================================================

class Classe(models.Model):

    NOM_CLASSES = [
        ("CM2", "CM2"),
        ("6ème", "6ème"),
        ("5ème", "5ème"),
        ("4ème", "4ème"),
        ("3ème", "3ème"),
        ("2nde", "2nde"),
        ("1ère", "1ère"),
        ("Terminale", "Terminale"),
    ]

    nom = models.CharField(
        max_length=20,
        choices=NOM_CLASSES,
        unique=True
    )

    def __str__(self):
        return self.nom


# ============================================================
# MATIÈRE
# ============================================================

class Matiere(models.Model):

    nom = models.CharField(
        max_length=100,
        unique=True
    )

    description = models.TextField(
        blank=True
    )

    def __str__(self):
        return self.nom


# ============================================================
# RELATION PROFESSEUR / MATIÈRE / CLASSE
# ============================================================

class Enseignement(models.Model):

    professeur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="enseignements",
        limit_choices_to={"role": "prof"}
    )

    matiere = models.ForeignKey(
        Matiere,
        on_delete=models.CASCADE,
        related_name="enseignements"
    )

    classe = models.ForeignKey(
        Classe,
        on_delete=models.CASCADE,
        related_name="enseignements"
    )

    actif = models.BooleanField(
        default=True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["professeur", "matiere", "classe"],
                name="unique_enseignement_prof_matiere_classe"
            )
        ]

    def __str__(self):
        return (
            f"{self.professeur.username} - "
            f"{self.matiere.nom} - "
            f"{self.classe.nom}"
        )


# ============================================================
# COURS
# ============================================================

class Cours(models.Model):

    titre = models.CharField(
        max_length=200
    )

    description = models.TextField(
        help_text="Résumé ou présentation du cours."
    )

    contenu = models.TextField(
        blank=True,
        help_text="Contenu pédagogique complet de la leçon."
    )

    document = models.FileField(
        upload_to="cours/documents/",
        blank=True,
        null=True,
        help_text="PDF, document Word ou autre support pédagogique."
    )

    date_publication = models.DateTimeField(
        auto_now_add=True
    )

    classe = models.ForeignKey(
        Classe,
        on_delete=models.CASCADE,
        related_name="cours",
        null=True,
        blank=True
    )

    matiere = models.ForeignKey(
        Matiere,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="cours"
    )

    professeur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={"role": "prof"},
        related_name="cours_crees"
    )

    def __str__(self):
        classe = self.classe.nom if self.classe else "Toutes classes"
        matiere = self.matiere.nom if self.matiere else "Sans matière"

        return f"{self.titre} - {matiere} ({classe})"


# ============================================================
# EXERCICE
# ============================================================

class Exercice(models.Model):

    cours = models.ForeignKey(
        Cours,
        on_delete=models.CASCADE,
        related_name="exercices"
    )

    titre = models.CharField(
        max_length=200
    )

    consigne = models.TextField(
        help_text="Énoncé ou consigne de l'exercice."
    )

    document = models.FileField(
        upload_to="exercices/documents/",
        blank=True,
        null=True,
        help_text="Document complémentaire de l'exercice."
    )

    date_publication = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.titre


# ============================================================
# DEVOIR
# ============================================================

class Devoir(models.Model):

    exercice = models.ForeignKey(
        Exercice,
        on_delete=models.CASCADE,
        related_name="devoirs"
    )

    titre = models.CharField(
        max_length=200
    )

    description = models.TextField(
        help_text="Consignes données aux élèves."
    )

    document = models.FileField(
        upload_to="devoirs/documents/",
        blank=True,
        null=True,
        help_text="Sujet ou document du devoir."
    )

    date_publication = models.DateTimeField(
        auto_now_add=True
    )

    date_limite = models.DateField()

    actif = models.BooleanField(
        default=True
    )

    def __str__(self):
        return self.titre


# ============================================================
# SOUMISSION D'UN ÉLÈVE
# ============================================================

class SoumissionDevoir(models.Model):

    STATUT_CHOICES = [
        ("soumis", "Soumis"),
        ("corrige", "Corrigé"),
        ("en_retard", "En retard"),
    ]

    devoir = models.ForeignKey(
        Devoir,
        on_delete=models.CASCADE,
        related_name="soumissions"
    )

    eleve = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="soumissions"
    )

    fichier = models.FileField(
        upload_to="soumissions/",
        blank=True,
        null=True,
        help_text="Copie de l'élève : PDF, Word ou autre fichier."
    )

    commentaire_eleve = models.TextField(
        blank=True,
        help_text="Commentaire éventuel de l'élève."
    )

    date_soumission = models.DateTimeField(
        auto_now_add=True
    )

    statut = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default="soumis"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["devoir", "eleve"],
                name="unique_soumission_devoir_eleve"
            )
        ]

    def __str__(self):
        return (
            f"{self.devoir.titre} - "
            f"{self.eleve.username}"
        )


# ============================================================
# CORRECTION
# ============================================================

class Correction(models.Model):

    soumission = models.OneToOneField(
        SoumissionDevoir,
        on_delete=models.CASCADE,
        related_name="correction",
        null=True,
        blank=True
    )

    professeur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="corrections",
        limit_choices_to={"role": "prof"}
    )

    note = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(20)
        ],
        help_text="Note sur 20."
    )

    commentaire = models.TextField(
        blank=True,
        help_text="Appréciation et conseils du professeur."
    )

    fichier_corrige = models.FileField(
        upload_to="corrections/",
        blank=True,
        null=True,
        help_text="Correction annotée ou corrigé transmis à l'élève."
    )

    date_correction = models.DateTimeField(
        auto_now_add=True,
        null=True,
        blank=True
    )

    def __str__(self):
        return (
            f"{self.soumission.devoir.titre if self.soumission else 'Sans soumission'} - "
            f"{self.soumission.eleve.username if self.soumission else 'Sans élève'} - "
            f"{self.note}/20"
        )


# ============================================================
# NOTIFICATION
# ============================================================

class Notification(models.Model):

    TYPE_CHOICES = [
        ("devoir", "Devoir"),
        ("correction", "Correction"),
        ("note", "Note"),
        ("information", "Information"),
    ]

    utilisateur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications"
    )

    titre = models.CharField(
        max_length=200
    )

    message = models.TextField()

    type_notification = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        default="information"
    )

    lu = models.BooleanField(
        default=False
    )

    date_creation = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.utilisateur.username} - {self.titre}"
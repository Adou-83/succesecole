from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import PermissionDenied
from django.db import models
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .decorators import role_required

from .forms import (
    CorrectionForm,
    CoursForm,
    DevoirForm,
    ExerciceForm,
    InscriptionForm,
    SoumissionDevoirForm,
)

from .models import (
    Correction,
    Cours,
    Devoir,
    Exercice,
    Notification,
    SoumissionDevoir,
)


# ============================================================
# AUTHENTIFICATION
# ============================================================

def register_view(request):
    if request.method == "POST":
        form = InscriptionForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("accueil")

    else:
        form = InscriptionForm()

    return render(
        request,
        "gestion/register.html",
        {
            "form": form,
        },
    )


def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(
            request,
            data=request.POST,
        )

        if form.is_valid():
            login(
                request,
                form.get_user(),
            )

            return redirect(
                request.GET.get("next") or "accueil"
            )

    else:
        form = AuthenticationForm()

    return render(
        request,
        "gestion/login.html",
        {
            "form": form,
        },
    )


@require_POST
def logout_view(request):
    logout(request)
    return redirect("login")


# ============================================================
# ACCUEIL
# ============================================================
@login_required
def accueil(request):
    if request.user.role == "prof":
        return redirect("tableau_professeur")

    if request.user.role == "parent":
        return redirect("suivi_parent")

    if request.user.role == "eleve":
        classe = request.user.classe

        cours_qs = Cours.objects.filter(
            classe=classe
        ).select_related(
            "classe",
            "matiere",
            "professeur"
        ).order_by("-date_publication") if classe else Cours.objects.none()

        devoirs_qs = Devoir.objects.filter(
            actif=True,
            exercice__cours__classe=classe
        ).select_related(
            "exercice",
            "exercice__cours",
            "exercice__cours__classe",
            "exercice__cours__matiere"
        ).order_by("date_limite") if classe else Devoir.objects.none()

        soumissions = SoumissionDevoir.objects.filter(
            eleve=request.user
        ).values_list("devoir_id", flat=True)

        devoirs_a_faire = devoirs_qs.exclude(
            id__in=soumissions
        )

        notifications_qs = Notification.objects.filter(
            utilisateur=request.user
        ).order_by("-date_creation")

        context = {
            "nombre_cours": cours_qs.count(),
            "nombre_exercices": Exercice.objects.filter(
                cours__classe=classe
            ).count() if classe else 0,
            "nombre_devoirs": devoirs_qs.count(),
            "nombre_notifications": notifications_qs.filter(lu=False).count(),
            "devoirs_a_faire": devoirs_a_faire[:10],
            "cours_recents": cours_qs[:6],
            "notifications_recentes": notifications_qs[:5],
        }

        return render(
            request,
            "gestion/accueil_eleve.html",
            context
        )

    return redirect("login")


# ============================================================
# COURS - LISTE
# ============================================================

@login_required
def liste_cours(request):
    user = request.user

    if user.role == "eleve":

        cours = Cours.objects.filter(
            classe=user.classe
        )

    elif user.role == "prof":

        cours = Cours.objects.filter(
            professeur=user
        )

    elif user.role == "parent":

        cours = (
            Cours.objects
            .filter(
                classe__eleves__in=user.enfants.all()
            )
            .distinct()
        )

    else:
        cours = Cours.objects.none()

    cours = (
        cours
        .select_related(
            "classe",
            "matiere",
            "professeur",
        )
        .order_by("-date_publication")
    )

    return render(
        request,
        "gestion/liste_cours.html",
        {
            "cours": cours,
        },
    )


# ============================================================
# COURS - DÉTAIL
# ============================================================

@login_required
def detail_cours(request, cours_id):
    cours = get_object_or_404(
        Cours.objects.select_related(
            "classe",
            "matiere",
            "professeur",
        ),
        pk=cours_id,
    )

    user = request.user
    autorise = False

    if user.role == "prof":

        autorise = (
            cours.professeur_id == user.id
        )

    elif user.role == "eleve":

        autorise = (
            cours.classe_id == user.classe_id
        )

    elif user.role == "parent":

        autorise = (
            cours.classe_id
            in user.enfants.values_list(
                "classe_id",
                flat=True,
            )
        )

    if not autorise:
        raise PermissionDenied

    exercices = (
        cours.exercices
        .all()
        .order_by("-date_publication")
    )

    return render(
        request,
        "gestion/detail_cours.html",
        {
            "cours": cours,
            "exercices": exercices,
        },
    )


# ============================================================
# COURS - CRÉER
# ============================================================

@login_required
@role_required("prof")
def creer_cours(request):

    if request.method == "POST":

        form = CoursForm(
            request.POST,
            request.FILES,
            professeur=request.user,
        )

        if form.is_valid():

            cours = form.save(commit=False)
            cours.professeur = request.user
            cours.save()

            return redirect(
                "detail_cours",
                cours_id=cours.id,
            )

    else:

        form = CoursForm(
            professeur=request.user
        )

    return render(
        request,
        "gestion/form_cours.html",
        {
            "form": form,
            "object": None,
            "titre_page": "Créer un cours",
            "bouton": "Créer le cours",
        },
    )


# ============================================================
# COURS - MODIFIER
# ============================================================

@login_required
@role_required("prof")
def modifier_cours(request, cours_id):

    cours = get_object_or_404(
        Cours,
        id=cours_id,
        professeur=request.user,
    )

    if request.method == "POST":

        form = CoursForm(
            request.POST,
            request.FILES,
            instance=cours,
            professeur=request.user,
        )

        if form.is_valid():

            form.save()

            return redirect(
                "detail_cours",
                cours_id=cours.id,
            )

    else:

        form = CoursForm(
            instance=cours,
            professeur=request.user,
        )

    return render(
        request,
        "gestion/form_cours.html",
        {
            "form": form,
            "object": cours,
            "cours": cours,
            "titre_page": "Modifier le cours",
            "bouton": "Enregistrer les modifications",
        },
    )


# ============================================================
# COURS - SUPPRIMER
# ============================================================

@login_required
@role_required("prof")
@require_POST
def supprimer_cours(request, cours_id):

    cours = get_object_or_404(
        Cours,
        id=cours_id,
        professeur=request.user,
    )

    cours.delete()

    return redirect("liste_cours")


# ============================================================
# EXERCICES - LISTE
# ============================================================

@login_required
def liste_exercices(request):

    user = request.user

    if user.role == "eleve":

        exercices = Exercice.objects.filter(
            cours__classe=user.classe
        )

    elif user.role == "prof":

        exercices = Exercice.objects.filter(
            cours__professeur=user
        )

    elif user.role == "parent":

        exercices = (
            Exercice.objects
            .filter(
                cours__classe__eleves__in=user.enfants.all()
            )
            .distinct()
        )

    else:

        exercices = Exercice.objects.none()

    exercices = (
        exercices
        .select_related(
            "cours",
            "cours__classe",
            "cours__matiere",
            "cours__professeur",
        )
        .order_by("-date_publication")
    )

    return render(
        request,
        "gestion/liste_exercices.html",
        {
            "exercices": exercices,
        },
    )


# ============================================================
# EXERCICE - CRÉER
# ============================================================

@login_required
@role_required("prof")
def creer_exercice(request):

    if request.method == "POST":

        form = ExerciceForm(
            request.POST,
            request.FILES,
            professeur=request.user,
        )

        if form.is_valid():

            exercice = form.save(commit=False)

            if exercice.cours.professeur_id != request.user.id:
                raise PermissionDenied

            exercice.save()

            return redirect(
                "detail_cours",
                cours_id=exercice.cours.id,
            )

    else:

        form = ExerciceForm(
            professeur=request.user
        )

    return render(
        request,
        "gestion/form_exercice.html",
        {
            "form": form,
            "object": None,
            "titre_page": "Créer un exercice",
            "bouton": "Créer l'exercice",
        },
    )


# ============================================================
# EXERCICE - MODIFIER
# ============================================================

@login_required
@role_required("prof")
def modifier_exercice(request, exercice_id):

    exercice = get_object_or_404(
        Exercice,
        id=exercice_id,
        cours__professeur=request.user,
    )

    if request.method == "POST":

        form = ExerciceForm(
            request.POST,
            request.FILES,
            instance=exercice,
            professeur=request.user,
        )

        if form.is_valid():

            form.save()

            return redirect(
                "detail_cours",
                cours_id=exercice.cours.id,
            )

    else:

        form = ExerciceForm(
            instance=exercice,
            professeur=request.user,
        )

    return render(
        request,
        "gestion/form_exercice.html",
        {
            "form": form,
            "object": exercice,
            "exercice": exercice,
            "titre_page": "Modifier l'exercice",
            "bouton": "Enregistrer les modifications",
        },
    )


# ============================================================
# EXERCICE - SUPPRIMER
# ============================================================

@login_required
@role_required("prof")
@require_POST
def supprimer_exercice(request, exercice_id):

    exercice = get_object_or_404(
        Exercice,
        id=exercice_id,
        cours__professeur=request.user,
    )

    cours_id = exercice.cours_id

    exercice.delete()

    return redirect(
        "detail_cours",
        cours_id=cours_id,
    )


# ============================================================
# TABLEAU DE BORD PROFESSEUR
# ============================================================

@login_required
@role_required("prof")
def tableau_professeur(request):

    cours_recents = (
        Cours.objects
        .filter(
            professeur=request.user
        )
        .select_related(
            "classe",
            "matiere",
        )
        .order_by("-date_publication")[:6]
    )

    nombre_cours = Cours.objects.filter(
        professeur=request.user
    ).count()

    nombre_exercices = Exercice.objects.filter(
        cours__professeur=request.user
    ).count()

    nombre_devoirs = Devoir.objects.filter(
        exercice__cours__professeur=request.user
    ).count()

    copies_a_corriger = SoumissionDevoir.objects.filter(
        devoir__exercice__cours__professeur=request.user,
        correction__isnull=True,
    ).count()

    devoirs_recents = (
        Devoir.objects
        .filter(
            exercice__cours__professeur=request.user
        )
        .select_related(
            "exercice",
            "exercice__cours",
            "exercice__cours__classe",
            "exercice__cours__matiere",
        )
        .annotate(
            nombre_soumissions=models.Count("soumissions")
        )
        .order_by("-date_publication")[:8]
    )

    return render(
        request,
        "gestion/tableau_professeur.html",
        {
            "cours_recents": cours_recents,
            "nombre_cours": nombre_cours,
            "nombre_exercices": nombre_exercices,
            "nombre_devoirs": nombre_devoirs,
            "copies_a_corriger": copies_a_corriger,
            "devoirs_recents": devoirs_recents,
        },
    )


# ============================================================
# DEVOIRS - CRÉER
# ============================================================

@login_required
@role_required("prof")
def creer_devoir(request):

    if request.method == "POST":

        form = DevoirForm(
            request.POST,
            request.FILES,
            professeur=request.user,
        )

        if form.is_valid():

            devoir = form.save(commit=False)

            exercice = devoir.exercice

            if exercice.cours.professeur_id != request.user.id:
                raise PermissionDenied

            devoir.save()

            return redirect("liste_devoirs")

    else:

        form = DevoirForm(
            professeur=request.user
        )

    return render(
        request,
        "gestion/form_devoir.html",
        {
            "form": form,
            "object": None,
            "creation": True,
            "titre_page": "Créer un devoir",
            "bouton": "Créer le devoir",
        },
    )


# ============================================================
# DEVOIRS - LISTE
# ============================================================

@login_required
@role_required(
    "eleve",
    "prof",
    "parent",
)
def liste_devoirs(request):

    user = request.user

    if user.role == "eleve":

        devoirs = Devoir.objects.filter(
            exercice__cours__classe=user.classe,
            actif=True,
        )

    elif user.role == "prof":

        devoirs = Devoir.objects.filter(
            exercice__cours__professeur=user
        )

    elif user.role == "parent":

        devoirs = (
            Devoir.objects
            .filter(
                exercice__cours__classe__eleves__in=user.enfants.all(),
                actif=True,
            )
            .distinct()
        )

    else:

        devoirs = Devoir.objects.none()

    devoirs = (
        devoirs
        .select_related(
            "exercice",
            "exercice__cours",
            "exercice__cours__matiere",
            "exercice__cours__classe",
        )
        .order_by("date_limite")
    )

    return render(
        request,
        "gestion/liste_devoirs.html",
        {
            "devoirs": devoirs,
        },
    )


# ============================================================
# DEVOIR - MODIFIER
# ============================================================

@login_required
@role_required("prof")
def modifier_devoir(request, devoir_id):

    devoir = get_object_or_404(
        Devoir,
        id=devoir_id,
        exercice__cours__professeur=request.user,
    )

    if request.method == "POST":

        form = DevoirForm(
            request.POST,
            request.FILES,
            instance=devoir,
            professeur=request.user,
        )

        if form.is_valid():

            form.save()

            return redirect("liste_devoirs")

    else:

        form = DevoirForm(
            instance=devoir,
            professeur=request.user,
        )

    return render(
        request,
        "gestion/form_devoir.html",
        {
            "form": form,
            "object": devoir,
            "creation": False,
            "devoir": devoir,
            "titre_page": "Modifier le devoir",
            "bouton": "Enregistrer les modifications",
        },
    )


# ============================================================
# DEVOIR - SUPPRIMER
# ============================================================

@login_required
@role_required("prof")
@require_POST
def supprimer_devoir(request, devoir_id):

    devoir = get_object_or_404(
        Devoir,
        id=devoir_id,
        exercice__cours__professeur=request.user,
    )

    devoir.delete()

    return redirect("liste_devoirs")


# ============================================================
# SOUMISSION ÉLÈVE
# ============================================================

@login_required
@role_required("eleve")
def soumettre_devoir(request, devoir_id):

    devoir = get_object_or_404(
        Devoir.objects.select_related(
            "exercice",
            "exercice__cours",
            "exercice__cours__classe",
        ),
        id=devoir_id,
        actif=True,
    )

    if not request.user.classe:
        raise PermissionDenied

    if devoir.exercice.cours.classe_id != request.user.classe_id:
        raise PermissionDenied

    if timezone.localdate() > devoir.date_limite:
        raise PermissionDenied

    submission_existante = (
        SoumissionDevoir.objects
        .filter(
            devoir=devoir,
            eleve=request.user,
        )
        .first()
    )

    if request.method == "POST":

        if submission_existante:
            form = SoumissionDevoirForm(
                request.POST,
                request.FILES,
                instance=submission_existante,
            )
        else:
            form = SoumissionDevoirForm(
                request.POST,
                request.FILES,
            )

        if form.is_valid():

            soumission = form.save(commit=False)
            soumission.devoir = devoir
            soumission.eleve = request.user
            soumission.statut = "soumis"
            soumission.save()

            Notification.objects.create(
                utilisateur=request.user,
                titre="Devoir envoyé",
                message=(
                    f"Votre devoir « {devoir.titre} » "
                    "a bien été envoyé."
                ),
                type_notification="devoir",
            )

            return redirect(
                "voir_devoir",
                devoir_id=devoir.id,
            )

    else:

        if submission_existante:
            form = SoumissionDevoirForm(
                instance=submission_existante
            )
        else:
            form = SoumissionDevoirForm()

    return render(
        request,
        "gestion/soumettre_devoir.html",
        {
            "form": form,
            "devoir": devoir,
            "exercice": devoir.exercice,
        },
    ) 


# ============================================================
# VOIR UN DEVOIR
# ============================================================

@login_required
def voir_devoir(request, devoir_id):
    devoir = get_object_or_404(
        Devoir.objects.select_related(
            "exercice",
            "exercice__cours",
            "exercice__cours__classe",
            "exercice__cours__matiere",
            "exercice__cours__professeur",
        ),
        id=devoir_id,
    )

    if request.user.role == "eleve":
        if not request.user.classe or devoir.exercice.cours.classe != request.user.classe:
            raise PermissionDenied

        soumission = SoumissionDevoir.objects.filter(
            devoir=devoir,
            eleve=request.user
        ).select_related("correction").first()

        return render(
            request,
            "gestion/voir_devoir.html",
            {
                "devoir": devoir,
                "soumission": soumission,
            },
        )

    if request.user.role == "prof":
        if devoir.exercice.cours.professeur != request.user:
            raise PermissionDenied

        return redirect("copies_devoir", devoir_id=devoir.id)

    raise PermissionDenied


# ============================================================
# COPIES D'UN DEVOIR
# ============================================================

@login_required
@role_required("prof")
def copies_devoir(request, devoir_id):

    devoir = get_object_or_404(
        Devoir.objects.select_related(
            "exercice",
            "exercice__cours",
            "exercice__cours__classe",
            "exercice__cours__matiere",
        ),
        id=devoir_id,
        exercice__cours__professeur=request.user,
    )

    soumissions = (
        SoumissionDevoir.objects
        .filter(
            devoir=devoir
        )
        .select_related(
            "eleve",
            "correction",
        )
        .order_by("-date_soumission")
    )

    copies_corrigees = soumissions.filter(
        correction__isnull=False
    ).count()

    copies_a_corriger = soumissions.filter(
        correction__isnull=True
    ).count()

    return render(
        request,
        "gestion/copies_devoir.html",
        {
            "devoir": devoir,
            "soumissions": soumissions,
            "copies_corrigees": copies_corrigees,
            "copies_a_corriger": copies_a_corriger,
        },
    )


# ============================================================
# CORRECTION D'UNE SOUMISSION
# ============================================================

@login_required
@role_required("prof")
def corriger_devoir(
    request,
    devoir_id,
    soumission_id,
):

    devoir = get_object_or_404(
        Devoir,
        id=devoir_id,
        exercice__cours__professeur=request.user,
    )

    soumission = get_object_or_404(
        SoumissionDevoir.objects.select_related(
            "eleve",
            "devoir",
        ),
        id=soumission_id,
        devoir=devoir,
    )

    correction = getattr(
        soumission,
        "correction",
        None,
    )

    if request.method == "POST":

        if correction:

            form = CorrectionForm(
                request.POST,
                request.FILES,
                instance=correction,
            )

        else:

            form = CorrectionForm(
                request.POST,
                request.FILES,
            )

        if form.is_valid():

            correction = form.save(
                commit=False
            )

            correction.soumission = soumission
            correction.professeur = request.user

            correction.save()

            soumission.statut = "corrige"

            soumission.save(
                update_fields=["statut"]
            )

            Notification.objects.create(
                utilisateur=soumission.eleve,
                titre="Devoir corrigé",
                message=(
                    f"Votre devoir « {devoir.titre} » "
                    "a été corrigé. "
                    f"Note : {correction.note}/20."
                ),
                type_notification="correction",
            )

            return redirect(
                "copies_devoir",
                devoir_id=devoir.id,
            )

    else:

        if correction:

            form = CorrectionForm(
                instance=correction
            )

        else:

            form = CorrectionForm()

    return render(
        request,
        "gestion/corriger_devoir.html",
        {
            "form": form,
            "devoir": devoir,
            "soumission": soumission,
            "correction": correction,
        },
    )


# ============================================================
# SUIVI PARENT
# ============================================================

@login_required
def suivi_parent(request):
    if request.user.role != "parent":
        raise PermissionDenied

    enfants = request.user.enfants.all().select_related("classe").order_by("username")

    enfants_data = []

    for enfant in enfants:
        cours = Cours.objects.filter(
            classe=enfant.classe
        ).select_related(
            "matiere",
            "professeur"
        ).order_by("-date_publication") if enfant.classe else Cours.objects.none()

        devoirs = Devoir.objects.filter(
            actif=True,
            exercice__cours__classe=enfant.classe
        ).select_related(
            "exercice",
            "exercice__cours",
            "exercice__cours__matiere"
        ).order_by("date_limite") if enfant.classe else Devoir.objects.none()

        soumissions = SoumissionDevoir.objects.filter(
            eleve=enfant
        ).select_related(
            "devoir",
            "correction",
            "devoir__exercice",
            "devoir__exercice__cours",
            "devoir__exercice__cours__matiere"
        ).order_by("-date_soumission")

        corrections = soumissions.filter(
            correction__isnull=False
        )

        notes = list(
            corrections.values_list(
                "correction__note",
                flat=True
            )
        )

        moyenne = None

        if notes:
            moyenne = sum(float(note) for note in notes) / len(notes)

        enfants_data.append({
            "enfant": enfant,
            "nombre_cours": cours.count(),
            "nombre_devoirs": devoirs.count(),
            "nombre_soumissions": soumissions.count(),
            "nombre_corriges": corrections.count(),
            "moyenne": moyenne,
            "soumissions_recentes": soumissions[:5],
        })

    return render(
        request,
        "gestion/suivi_parent.html",
        {
            "enfants_data": enfants_data,
        },
    )

# ============================================================
# NOTIFICATIONS
# ============================================================

@login_required
def notifications(request):
    notifications_qs = Notification.objects.filter(
        utilisateur=request.user
    ).order_by("-date_creation")

    return render(
        request,
        "gestion/notifications.html",
        {
            "notifications": notifications_qs,
        },
    )

@login_required
def marquer_notification_lue(request, notification_id):
    notification = get_object_or_404(
        Notification,
        id=notification_id,
        utilisateur=request.user,
    )

    notification.lu = True
    notification.save(update_fields=["lu"])

    return redirect("notifications")
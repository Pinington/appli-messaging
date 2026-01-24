from django.db import models
from django.contrib.auth.models import User

# 1. Modèle "Salon" (Room)
class Salon(models.Model):
    nom = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    createur = models.ForeignKey(User, on_delete=models.CASCADE, related_name="salons_crees")
    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nom


# 2. Modèle "SalonMember" (pour les rôles)
class SalonMember(models.Model):
    ROLE_CHOICES = [
        ('creator', 'Créateur'),
        ('moderator', 'Modérateur'),
        ('member', 'Membre'),
    ]
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE, related_name='membres')
    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE, related_name='salons_rejoints')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member')
    date_rejoint = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('salon', 'utilisateur')

    def __str__(self):
        return f"{self.utilisateur.username} - {self.salon.nom} ({self.role})"


# 3. Modèle "Message"
class Message(models.Model):
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE, related_name='messages')
    auteur = models.ForeignKey(User, on_delete=models.CASCADE, related_name='messages_envoyes')
    contenu = models.TextField()
    emojis = models.CharField(max_length=255, blank=True, null=True)
    date_envoi = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.auteur.username} - {self.contenu[:20]}..."

    class Meta:
        ordering = ['date_envoi']

## 4. Modele "Ban"
class Ban(models.Model):
    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE)
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE)
    date_ban = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('utilisateur', 'salon')
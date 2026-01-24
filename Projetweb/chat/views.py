from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Salon, SalonMember, Message, Ban
from django.urls import reverse  
from django.http import JsonResponse


def is_salon_admin(user, salon):
    return SalonMember.objects.filter(
        salon=salon,
        utilisateur=user,
        role='creator'
    ).exists()


@login_required(login_url="accounts:login")
def home(request):
    rooms = Salon.objects.all()
    active_room_id = request.GET.get("room")
    
    messages = []
    active_room = None
    is_admin = False  # NEW: default

    if active_room_id:
        try:
            active_room = Salon.objects.get(id=active_room_id)

            # Vérifier le ban AVANT de récupérer les messages
            if Ban.objects.filter(utilisateur=request.user, salon=active_room).exists():
                from django.contrib import messages
                messages.error(request, "Vous êtes banni de ce salon")
                return redirect('chat:home')  # ← stoppe ici

            messages = Message.objects.filter(salon=active_room).order_by('date_envoi')[:50]
            is_admin = is_salon_admin(request.user, active_room)

        except Salon.DoesNotExist:
            pass
    
    return render(request, "home.html", {
        "rooms": rooms,
        "active_room": active_room,
        "messages": messages,
        "active_room_id": active_room_id,
        "is_admin": is_admin,  # NEW: pass to template
    })


@login_required(login_url="accounts:login")
def create_room(request):
    if request.method == 'POST':
        nom = request.POST.get('nom')
        description = request.POST.get('description', '')
        salon = Salon.objects.create(
            nom=nom,
            description=description,
            createur=request.user
        )
        SalonMember.objects.create(
            salon=salon,
            utilisateur=request.user,
            role='creator'
        )
        return redirect('chat:home')
    return render(request, 'create_room.html')


@login_required
def send_message(request):
    if request.method == 'POST':
        room_id = request.POST.get('room_id')
        content = request.POST.get('content')

        if not room_id or not content:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'error': 'Données manquantes'}, status=400)
            return redirect('chat:home')
        
        try:
            salon = Salon.objects.get(id=room_id)

            if Ban.objects.filter(utilisateur=request.user, salon=salon).exists():
                return JsonResponse({'success': False, 'error': "Vous êtes banni de ce salon"})

            message = Message.objects.create(
                salon=salon,
                auteur=request.user,
                contenu=content
            )
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message_id': message.id,
                    'author': request.user.username,
                    'content': content,
                    'timestamp': message.date_envoi.strftime('%H:%M'),
                    'is_me': True
                })
            
        except Salon.DoesNotExist:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'error': 'Salon non trouvé'}, status=404)
    
    
    return redirect(f"{reverse('chat:home')}?room={room_id}")


@login_required
def delete_message(request, message_id):
    message = Message.objects.get(id=message_id)
    salon = message.salon

    if not is_salon_admin(request.user, salon):
        return JsonResponse({'error': 'Permission denied'}, status=403)

    message.delete()
    return JsonResponse({'success': True})


@login_required
def ban_user(request, salon_id, user_id):
    salon = Salon.objects.get(id=salon_id)

    # Vérifie que c'est un admin
    if not is_salon_admin(request.user, salon):
        return JsonResponse({'error': 'Permission denied'}, status=403)

    # Ne pas se bannir soi-même
    if request.user.id == int(user_id):
        return JsonResponse({'error': "Vous ne pouvez pas vous bannir vous-même"}, status=400)

    # Crée un ban
    Ban.objects.get_or_create(utilisateur_id=user_id, salon=salon)

    # Supprime de SalonMember pour éviter qu'il reste membre
    SalonMember.objects.filter(salon=salon, utilisateur_id=user_id).delete()

    return JsonResponse({'success': True})


@login_required
def delete_salon(request, salon_id):
    salon = Salon.objects.get(id=salon_id)

    if salon.createur != request.user:
        return JsonResponse({'error': 'Permission denied'}, status=403)

    salon.delete()
    return redirect('chat:home')


def get_messages_json(request, room_id):
    try:
        salon = Salon.objects.get(id=room_id)
    except Salon.DoesNotExist:
        return JsonResponse({'error': 'Salon non trouvé'}, status=404)

    # Vérification du ban
    if Ban.objects.filter(utilisateur=request.user, salon=salon).exists():
        return JsonResponse({'error': "Vous êtes banni de ce salon"}, status=403)

    messages = Message.objects.filter(salon=salon).order_by('date_envoi')[:20]
    
    messages_list = []
    for msg in messages:
        messages_list.append({
            'author': msg.auteur.username,
            'content': msg.contenu,
            'time': msg.date_envoi.strftime('%H:%M'),
        })
    
    return JsonResponse({'messages': messages_list})
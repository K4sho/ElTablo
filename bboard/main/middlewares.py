from .models import SubRubric


def bboard_context_processor(request):
    """Обработчик контекста"""
    context = {}
    context['rubrics'] = SubRubric.objects.all()
    return context
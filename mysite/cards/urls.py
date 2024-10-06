from django.urls import path, re_path, reverse_lazy
from . import views

app_name = 'cards'
urlpatterns = [
    path('', views.WordListView.as_view(), name='all'),
    path('word/<int:pk>', views.WordDetailView.as_view(), name='word_detail'),
    path('word/create', views.WordCreateView.as_view(success_url=reverse_lazy('cards:all')), name='word_create'),
    path('word/<int:pk>/update', views.WordUpdateView.as_view(success_url=reverse_lazy('cards:all')),
         name='word_update'),
    path('word/<int:pk>/delete', views.WordDeleteView.as_view(success_url=reverse_lazy('cards:all')),
         name='word_delete'),
    path('word/<int:pk>/meaning', views.MeaningCreateView.as_view(success_url=reverse_lazy(
        'cards:word_detail')), name='word_meaning_create'),
    path('word_meaning/<int:pk>', views.CrossDetailView.as_view(), name='word_meaning_detail'),
    path('word_meaning/<int:pk>/delete', views.CrossDeleteView.as_view(success_url=reverse_lazy('cards:word_detail')),
         name='word_meaning_delete'),
    path('word_meaning/<int:pk>/update', views.CrossUpdateView.as_view(success_url=reverse_lazy('cards:word_detail')),
         name='word_meaning_update'),
    path('word_meaning/<int:pk>/comment', views.CommentCreateView.as_view(success_url=reverse_lazy(
        'cards:word_meaning_detail')), name='word_meaning_comment_create'),
    path('meaning/<int:pk>/delete', views.MeaningDeleteView.as_view(success_url=reverse_lazy('cards:meaning_list')),
         name='meaning_delete'),
    path('comment/<int:pk>/delete',
         views.CommentDeleteView.as_view(success_url=reverse_lazy('cards:word_meaning_detail')),
         name='word_meaning_comment_delete'),
    path('comment/<int:pk>/update',
         views.CommentUpdateView.as_view(success_url=reverse_lazy('cards:word_meaning_detail')),
         name='word_meaning_comment_update'),
    path('tag_group_words/', views.TagGroupsView.as_view(), name='tag_group_words_get'),
    path('tag_group_words/<str:tag_name>/<str:mix_up>/<int:first>/<int:last>/<str:field>/<str:show>/',
         views.TagGroupsView.as_view(), name='tag_group_words'),
    path('meaning_list', views.MeaningListView.as_view(), name='meaning_list'),
    path('meaning/<int:pk>', views.MeaningDetailView.as_view(), name='meaning_detail'),
]

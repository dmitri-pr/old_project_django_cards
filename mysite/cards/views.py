import json
from copy import deepcopy

from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import generic
from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView

from cards.forms import CreateForm, MeaningForm, CommentForm, CrossMeaningUpdateForm, CommentUpdateForm, TagAddForm
from cards.models import Word, Meaning, CrossTable, Comment, Tag
from cards.owner import OwnerListView, OwnerDetailView, OwnerCreateView, OwnerUpdateView, OwnerWordDeleteView, \
    OwnerMeaningDeleteView, OwnerCrossDeleteView, OwnerCommentDeleteView, OwnerCrossUpdateView, \
    OwnerCommentUpdateView
from django.urls import reverse
from django.contrib.humanize.templatetags.humanize import naturaltime

from cards.utils import dump_queries

from django.db.models import Q

from random import shuffle


class WordListView(OwnerListView):
    model = Word
    template_name = "cards/word_list.html"

    def get(self, request):
        word_list = None
        searching = None
        word_groups = None
        if request.user.is_authenticated:
            searching = request.GET.get("search", False)
            if searching:
                query = Q(writing__icontains=searching)
                query.add(Q(old_writing__icontains=searching), Q.OR)
                query.add(Q(transcription__icontains=searching), Q.OR)
                query.add(Q(tags__name__in=[searching]), Q.OR)
                word_list = Word.objects.filter(query, owner=self.request.user).select_related().distinct().order_by(
                    '-updated_at')[:10000]
            else:
                word_list = Word.objects.filter(owner=self.request.user).order_by('-updated_at')[:10000]

            for obj in word_list:
                obj.natural_updated = naturaltime(obj.updated_at)

            word_groups = Tag.objects.filter(owner=self.request.user)

        ctx = {'word_list': word_list, 'search': searching, 'word_groups': word_groups}
        return render(request, self.template_name, ctx)


class WordDetailView(OwnerDetailView):
    model = Word
    template_name = "cards/word_detail.html"

    def get(self, request, pk):
        word = Word.objects.get(id=pk)
        cross_objs = list(CrossTable.objects.filter(word=word).order_by('-meaning__updated_at'))
        l_all = list()
        for cross_obj in cross_objs:
            l_comms = list()
            for el in list(cross_obj.comment_set.all()):
                if len(el.text) < 21:
                    l_comms.append(el.text)
                else:
                    l_comms.append((el.text[:17] + '...'))
            l_comms = ', '.join(l_comms)
            l_all.append((cross_obj, l_comms))
        meaning_form = MeaningForm()
        context = {
            'word': word,
            'cross_objs_all': l_all,
            'cross_objs': cross_objs,
            'meaning_form': meaning_form}
        return render(request, self.template_name, context)


class WordCreateView(LoginRequiredMixin, View):
    template_name = 'cards/word_form.html'
    success_url = reverse_lazy('cards:all')

    def get(self, request, pk=None):
        form = CreateForm(initial={'tags': '0, '})
        ctx = {'form': form}
        return render(request, self.template_name, ctx)

    def post(self, request, pk=None):
        form = CreateForm(request.POST)

        if not '0' in request.POST['tags']:
            err = "Enter '0' into tags-field"
            ctx = {'form': form, 'err': err}
            return render(request, self.template_name, ctx)

        if not form.is_valid():
            err = "Fill correctly all the fields"
            ctx = {'form': form, 'err': err}
            return render(request, self.template_name, ctx)

        if not Word.objects.filter(writing=request.POST['writing'], old_writing=request.POST['old_writing'],
                                   transcription=request.POST['transcription'], owner=request.user):
            word = form.save(commit=False)
            word.owner = self.request.user
            word.save()
            form.save_m2m()

            for tag in word.tags.all():
                Tag.objects.get_or_create(text=tag, owner=self.request.user)

        return redirect(self.success_url)


class WordUpdateView(LoginRequiredMixin, View):
    template_name = 'cards/word_form.html'
    success_url = reverse_lazy('cards:all')

    def get(self, request, pk):
        word = get_object_or_404(Word, id=pk, owner=self.request.user)
        form = CreateForm(instance=word)
        ctx = {'form': form}
        return render(request, self.template_name, ctx)

    def post(self, request, pk=None):
        word = get_object_or_404(Word, id=pk, owner=self.request.user)
        form = CreateForm(request.POST, instance=word)

        if not '0' in request.POST['tags']:
            err = "Enter '0' into tags-field"
            ctx = {'form': form, 'err': err}
            return render(request, self.template_name, ctx)

        if not form.is_valid():
            err = "Fill correctly all the fields"
            ctx = {'form': form, 'err': err}
            return render(request, self.template_name, ctx)

        word = form.save(commit=False)
        word.save()
        form.save_m2m()

        for tag in word.tags.all():
            Tag.objects.get_or_create(text=tag, owner=self.request.user)

        return redirect(self.success_url)


class WordDeleteView(OwnerWordDeleteView):
    model = Word


class MeaningDeleteView(OwnerMeaningDeleteView):
    model = Meaning


class MeaningCreateView(LoginRequiredMixin, View):
    success_url = reverse_lazy('cards:word_detail')

    def post(self, request, pk):
        word = get_object_or_404(Word, id=pk)
        meaning, created = Meaning.objects.get_or_create(text=request.POST['meaning'], owner=self.request.user)
        CrossTable.objects.get_or_create(word=word, meaning=meaning, username=request.user.username)
        return redirect(reverse('cards:word_detail', args=[pk]))


class CrossUpdateView(OwnerCrossUpdateView):
    template_name = 'cards/crosstable_form.html'

    def get(self, request, pk):
        crosstable = get_object_or_404(CrossTable, id=pk, username=self.request.user.username)
        form = CrossMeaningUpdateForm(instance=crosstable.meaning)
        ctx = {'form': form, 'crosstable': crosstable}
        return render(request, self.template_name, ctx)

    def post(self, request, pk=None):
        crosstable = get_object_or_404(CrossTable, id=pk, username=self.request.user.username)
        form = CrossMeaningUpdateForm(request.POST, instance=crosstable.meaning)

        if not form.is_valid():
            ctx = {'form': form, 'crosstable': crosstable}
            return render(request, self.template_name, ctx)

        cross_meaning_text = form.save(commit=False)
        try:
            cross_meaning_text.save()
            form.save_m2m()
        except:
            word = crosstable.word
            meaning = Meaning.objects.get(text=cross_meaning_text, owner=self.request.user)
            CrossTable.objects.filter(id=pk, username=self.request.user.username).delete()
            CrossTable.objects.get_or_create(word=word, meaning=meaning, username=request.user.username)
        return redirect(reverse('cards:word_detail', args=[crosstable.word.id]))


class CrossDeleteView(OwnerCrossDeleteView):
    model = CrossTable
    template_name = "cards/word_meaning_delete.html"

    def get_success_url(self):
        word = self.object.word
        return reverse('cards:word_detail', args=[word.id])


class CommentCreateView(LoginRequiredMixin, View):
    success_url = reverse_lazy('cards:word_meaning_detail')

    def post(self, request, pk):
        word_meaning = get_object_or_404(CrossTable, id=pk)
        comment = Comment(text=request.POST['comment'], owner=self.request.user, word_meaning=word_meaning)
        comment.save()
        return redirect(reverse('cards:word_meaning_detail', args=[pk]))


class CommentUpdateView(OwnerCommentUpdateView):
    template_name = 'cards/comment_form.html'

    def get(self, request, pk):
        comment = get_object_or_404(Comment, id=pk, owner=self.request.user)
        form = CommentUpdateForm(instance=comment)
        ctx = {'form': form, 'comment': comment}
        return render(request, self.template_name, ctx)

    def post(self, request, pk=None):
        comment = get_object_or_404(Comment, id=pk, owner=self.request.user)
        form = CommentUpdateForm(request.POST, instance=comment)

        if not form.is_valid():
            ctx = {'form': form, 'comment': comment}
            return render(request, self.template_name, ctx)

        comment_text = form.save(commit=False)
        comment_text.save()
        form.save_m2m()

        return redirect(reverse('cards:word_meaning_detail', args=[comment.word_meaning.id]))


class CommentDeleteView(OwnerCommentDeleteView):
    model = Comment
    template_name = "cards/comment_delete.html"

    def get_success_url(self):
        word_meaning = self.object.word_meaning
        return reverse('cards:word_meaning_detail', args=[word_meaning.id])


class CrossDetailView(OwnerDetailView):
    model = CrossTable
    template_name = "cards/word_meaning_detail.html"

    def get(self, request, pk):
        crosstable = CrossTable.objects.get(id=pk)
        comments = Comment.objects.filter(word_meaning=crosstable)
        comment_form = CommentForm()
        context = {'crosstable': crosstable, 'comments': comments, 'comment_form': comment_form}
        return render(request, self.template_name, context)


class TagGroupsView(View):
    template_name = "cards/tag_words.html"

    def get(self, request, tag_name=None, mix_up='no', first=None, last=None, field=None, show=None):
        if not tag_name:
            tag_name = request.GET.get('tag_name', '')
            mix_up = request.GET.get('mix_up', 'no')
            first = int(request.GET.get('first', 1))
            last = int(request.GET.get('last', 10000))
            field = request.GET.get('field', 'writing')
            show = int(request.GET.get('show', 30))
        tag_group_words = Word.objects.filter(tags__name=tag_name, owner=self.request.user)[first - 1:last]
        tag_group_words = list(tag_group_words)
        if tag_group_words:
            if mix_up == 'yes':
                shuffle(tag_group_words)
        if show:
            try:
                tag_group_words = tag_group_words[:int(show)]
            except:
                tag_group_words = tag_group_words[:30]
        # dicts = deepcopy(tag_group_words)
        # l_dicts = list()
        # for el in dicts:
        #     el.__dict__.pop('_state')
        #     el.__dict__.pop('created_at')
        #     el.__dict__.pop('updated_at')
        #     l_dicts.append(el.__dict__)
        #     print(el.__dict__)
        #     print(l_dicts)
        # json_string = json.dumps(l_dicts)
        # print(json_string)
        # print(l_dicts)

        word_groups = Tag.objects.filter(owner=self.request.user)

        if not Word.objects.filter(tags__name=tag_name, owner=self.request.user):
            Tag.objects.filter(text=tag_name, owner=self.request.user).delete()

        cross_table_objs = CrossTable.objects.all()

        tag_add_form = TagAddForm()

        context = {'tag_group_words': tag_group_words, 'tag_name': tag_name, 'mix_up': mix_up,
                   'word_groups': word_groups, 'first': first, 'last': last,
                   'field': field, 'cross_table_objs': cross_table_objs, 'tag_add_form': tag_add_form, 'show': show}
        return render(request, self.template_name, context)

    def post(self, request, tag_name, mix_up, first, last, field, show):
        if 'new_tag' in request.POST:
            if request.POST['new_tag']:
                Tag.objects.get_or_create(text=request.POST['new_tag'], owner=self.request.user)
                tag_group_words = Word.objects.filter(tags__name=tag_name, owner=self.request.user)[first - 1:last]
                for word in tag_group_words:
                    if not request.POST['new_tag'] in word.tags.all():
                        word.tags.add(request.POST['new_tag'])
                        word.save()
            return redirect(reverse('cards:tag_group_words', args=[request.POST['new_tag'], "no", 1, 10000, 'writing',
                                                                   'show']))
        if 'delete_tag' in request.POST:
            if request.POST['delete_tag']:
                tag_group_words = Word.objects.filter(tags__name=tag_name, owner=self.request.user)[first - 1:last]
                for word in tag_group_words:
                    word.tags.remove(request.POST['delete_tag'])
                    word.save()
            if not Word.objects.filter(tags__name=request.POST['delete_tag'], owner=self.request.user):
                Tag.objects.filter(text=request.POST['delete_tag'], owner=self.request.user).delete()
            return redirect(reverse('cards:tag_group_words', args=['0', 'no', 1, 10000, 'writing', 'show']))


class MeaningListView(OwnerListView):
    model = Meaning
    template_name = "cards/meaning_list.html"

    def get(self, request):
        meaning_list = None
        searching = None
        if request.user.is_authenticated:
            searching = request.GET.get("search", False)
            if searching:
                query = Q(text__icontains=searching)
                meaning_list = Meaning.objects.filter(query, owner=self.request.user).select_related().distinct(
                ).order_by('-updated_at')[:10000]
            else:
                meaning_list = Meaning.objects.filter(owner=self.request.user).order_by('-updated_at')[:10000]

            for obj in meaning_list:
                obj.natural_updated = naturaltime(obj.updated_at)

        ctx = {'meaning_list': meaning_list, 'search': searching}
        return render(request, self.template_name, ctx)


class MeaningDetailView(OwnerDetailView):
    model = Meaning
    template_name = "cards/meaning_detail.html"

    def get(self, request, pk):
        meaning = Meaning.objects.get(id=pk)
        words = list(meaning.word_set.all().order_by('-updated_at'))
        context = {
            'meaning': meaning,
            'words': words}
        return render(request, self.template_name, context)

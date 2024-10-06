from django.views.generic import CreateView, UpdateView, DeleteView, ListView, DetailView

from django.contrib.auth.mixins import LoginRequiredMixin


class OwnerListView(ListView):
    """ """


class OwnerDetailView(DetailView):
    """ """


class OwnerCreateView(LoginRequiredMixin, CreateView):
    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.owner = self.request.user
        obj.save()
        form.save_m2m()
        return super(OwnerCreateView, self).form_valid(form)


class OwnerUpdateView(LoginRequiredMixin, UpdateView):
    def get_queryset(self):
        qs = super(OwnerUpdateView, self).get_queryset()
        return qs.filter(owner=self.request.user)


class OwnerCrossUpdateView(LoginRequiredMixin, UpdateView):
    def get_queryset(self):
        qs = super(OwnerCrossUpdateView, self).get_queryset()
        return qs.filter(username=self.request.user.username)


class OwnerWordDeleteView(LoginRequiredMixin, DeleteView):
    def get_queryset(self):
        qs = super(OwnerWordDeleteView, self).get_queryset()
        return qs.filter(owner=self.request.user)


class OwnerCrossDeleteView(LoginRequiredMixin, DeleteView):
    def get_queryset(self):
        qs = super(OwnerCrossDeleteView, self).get_queryset()
        return qs.filter(username=self.request.user.username)


class OwnerMeaningDeleteView(LoginRequiredMixin, DeleteView):
    def get_queryset(self):
        qs = super(OwnerMeaningDeleteView, self).get_queryset()
        return qs.filter(owner=self.request.user)


class OwnerCommentUpdateView(LoginRequiredMixin, UpdateView):
    def get_queryset(self):
        qs = super(OwnerCommentUpdateView, self).get_queryset()
        return qs.filter(owner=self.request.user)


class OwnerCommentDeleteView(LoginRequiredMixin, DeleteView):
    def get_queryset(self):
        qs = super(OwnerCommentDeleteView, self).get_queryset()
        return qs.filter(owner=self.request.user)


class OwnerMeaningListView(ListView):
    """ """

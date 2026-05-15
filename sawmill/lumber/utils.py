menu = [
    {"title": "Главная", "url_name": "home"},
    {"title": "О предприятии", "url_name": "about"},
    {"title": "Добавить товар", "url_name": "addpage"},
    {"title": "Ручная форма", "url_name": "addpage_raw"},
]


class DataMixin:
    paginate_by = 2
    title_page = None

    def get_mixin_context(self, context, **kwargs):
        context["menu"] = menu
        context["cat_selected"] = None
        context["tag_selected"] = None
        if self.title_page:
            context["title"] = self.title_page
        context.update(kwargs)
        return context
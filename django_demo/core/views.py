from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from .forms import ArticleForm, CommentForm, LoginForm, PreferenceForm, ProfileForm, RegisterForm
from .models import Article, Category, Comment, EventLog


def _ensure_default_categories():
    defaults = ["General", "Technology", "Academic"]
    for name in defaults:
        Category.objects.get_or_create(name=name)


def home_view(request):
    published_articles = Article.objects.filter(status=Article.PUBLISHED)
    context = {
        "recent_articles": published_articles[:5],
        "article_count": published_articles.count(),
        "category_count": Category.objects.count(),
    }
    return render(request, "core/home.html", context)


def concepts_view(request):
    relational_items = {
        "articles": Article.objects.count(),
        "comments": Comment.objects.count(),
        "users": User.objects.count(),
    }
    nosql_style_items = EventLog.objects.all()[:10]
    return render(
        request,
        "core/concepts.html",
        {
            "relational_items": relational_items,
            "nosql_style_items": nosql_style_items,
        },
    )


def article_list_view(request):
    query = request.GET.get("q", "").strip()
    base_qs = Article.objects.select_related("author", "category").filter(status=Article.PUBLISHED)
    if query:
        base_qs = base_qs.filter(Q(title__icontains=query) | Q(body__icontains=query))

    per_page = request.session.get("results_per_page", 5)
    articles = base_qs[:per_page]

    return render(
        request,
        "core/articles/list.html",
        {
            "articles": articles,
            "query": query,
            "per_page": per_page,
        },
    )


def article_detail_view(request, slug):
    article = get_object_or_404(Article.objects.select_related("author", "category"), slug=slug)
    article.view_count += 1
    article.save(update_fields=["view_count"])

    EventLog.objects.create(
        actor=request.user if request.user.is_authenticated else None,
        event_type="article_view",
        payload={"article_id": article.id, "path": request.path},
    )

    return render(
        request,
        "core/articles/detail.html",
        {
            "article": article,
            "comment_form": CommentForm(),
        },
    )


@login_required
@require_http_methods(["GET", "POST"])
def article_create_view(request):
    _ensure_default_categories()

    if request.method == "POST":
        form = ArticleForm(request.POST)
        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user
            article.save()
            EventLog.objects.create(
                actor=request.user,
                event_type="article_created",
                payload={"article_id": article.id, "title": article.title},
            )
            messages.success(request, "Article created.")
            return redirect(article.get_absolute_url())
    else:
        form = ArticleForm()
    return render(request, "core/articles/form.html", {"form": form, "title": "Create Article"})


@login_required
@require_http_methods(["GET", "POST"])
def article_edit_view(request, slug):
    article = get_object_or_404(Article, slug=slug)
    if article.author != request.user:
        messages.error(request, "You are not allowed to edit this article.")
        return redirect(article.get_absolute_url())

    if request.method == "POST":
        form = ArticleForm(request.POST, instance=article)
        if form.is_valid():
            form.save()
            EventLog.objects.create(
                actor=request.user,
                event_type="article_updated",
                payload={"article_id": article.id},
            )
            messages.success(request, "Article updated.")
            return redirect(article.get_absolute_url())
    else:
        form = ArticleForm(instance=article)

    return render(request, "core/articles/form.html", {"form": form, "title": "Edit Article"})


@login_required
@require_http_methods(["POST"])
def article_delete_view(request, slug):
    article = get_object_or_404(Article, slug=slug)
    if article.author != request.user:
        messages.error(request, "You are not allowed to delete this article.")
        return redirect(article.get_absolute_url())

    article_title = article.title
    article.delete()
    EventLog.objects.create(
        actor=request.user,
        event_type="article_deleted",
        payload={"title": article_title},
    )
    messages.success(request, "Article deleted.")
    return redirect("core:article_list")


@login_required
@require_http_methods(["POST"])
def comment_create_view(request, slug):
    article = get_object_or_404(Article, slug=slug)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.article = article
        comment.author = request.user
        comment.save()
        messages.success(request, "Comment added.")
    else:
        messages.error(request, "Invalid comment data.")
    return redirect(article.get_absolute_url())


@login_required
@require_http_methods(["GET", "POST"])
def profile_view(request):
    profile = request.user.profile
    if request.method == "POST":
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated.")
            return redirect("core:profile")
    else:
        form = ProfileForm(instance=profile)
    return render(request, "core/profile.html", {"form": form})


@require_http_methods(["GET", "POST"])
def register_view(request):
    if request.user.is_authenticated:
        return redirect("core:dashboard")

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful.")
            return redirect("core:dashboard")
    else:
        form = RegisterForm()

    return render(request, "core/auth/register.html", {"form": form})


@require_http_methods(["GET", "POST"])
def login_view(request):
    if request.user.is_authenticated:
        return redirect("core:dashboard")

    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            if not form.cleaned_data.get("remember_me"):
                request.session.set_expiry(0)
            EventLog.objects.create(actor=user, event_type="user_login", payload={"ip": request.META.get("REMOTE_ADDR")})
            return redirect("core:dashboard")
    else:
        form = LoginForm(request)

    return render(request, "core/auth/login.html", {"form": form})


@login_required
def dashboard_view(request):
    request.session["dashboard_visits"] = request.session.get("dashboard_visits", 0) + 1
    response = render(
        request,
        "core/dashboard.html",
        {
            "my_articles": request.user.articles.all()[:5],
            "visit_count": request.session.get("dashboard_visits", 0),
        },
    )
    response.set_cookie("last_dashboard", "seen", max_age=60 * 60 * 24, httponly=True, samesite="Lax")
    return response


@login_required
@require_http_methods(["GET", "POST"])
def preferences_view(request):
    if request.method == "POST":
        form = PreferenceForm(request.POST)
        if form.is_valid():
            request.session["results_per_page"] = form.cleaned_data["results_per_page"]
            request.session["compact_mode"] = form.cleaned_data["compact_mode"]
            messages.success(request, "Preferences saved in session.")
            return redirect("core:article_list")
    else:
        form = PreferenceForm(
            initial={
                "results_per_page": request.session.get("results_per_page", 5),
                "compact_mode": request.session.get("compact_mode", False),
            }
        )
    return render(request, "core/preferences.html", {"form": form})


def articles_api_view(request):
    items = list(
        Article.objects.filter(status=Article.PUBLISHED)
        .values("id", "title", "slug", "author__username", "category__name")[:10]
    )
    return JsonResponse({"count": len(items), "results": items})

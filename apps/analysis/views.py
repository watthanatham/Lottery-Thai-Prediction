"""
Views for Thai Government Lottery Analysis App
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_POST, require_GET
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count, Q
from datetime import datetime

from .models import LotteryDraw, FormulaConfig, AnalysisSession, PredictionEntry
from .forms import LotteryDrawForm, AnalysisRunForm
from .formulas import FormulaEngine


# ============================================================
# Dashboard
# ============================================================
def dashboard(request):
    draws = LotteryDraw.objects.all()[:10]
    total_draws = LotteryDraw.objects.count()
    total_sessions = AnalysisSession.objects.count()

    # Accuracy stats
    correct = PredictionEntry.objects.filter(is_verified=True, was_correct=True).count()
    verified = PredictionEntry.objects.filter(is_verified=True).count()
    accuracy = round(correct / verified * 100, 1) if verified else 0

    recent_sessions = AnalysisSession.objects.select_related('reference_draw').all()[:5]

    return render(request, 'analysis/dashboard.html', {
        'draws': draws,
        'total_draws': total_draws,
        'total_sessions': total_sessions,
        'accuracy': accuracy,
        'correct': correct,
        'verified': verified,
        'recent_sessions': recent_sessions,
    })


# ============================================================
# Lottery Draws — CRUD
# ============================================================
def draw_list(request):
    draws = LotteryDraw.objects.all()
    return render(request, 'analysis/draw_list.html', {'draws': draws})


def draw_add(request):
    if request.method == 'POST':
        form = LotteryDrawForm(request.POST)
        if form.is_valid():
            draw = form.save()
            messages.success(request, f'Draw {draw.draw_date} saved successfully.')
            if request.htmx:
                return HttpResponse(
                    f'<div class="toast-success">Draw {draw.draw_date} saved!</div>',
                    headers={'HX-Redirect': '/draws/'}
                )
            return redirect('draw_list')
    else:
        form = LotteryDrawForm()
    return render(request, 'analysis/draw_form.html', {'form': form, 'action': 'Add'})


def draw_edit(request, pk):
    draw = get_object_or_404(LotteryDraw, pk=pk)
    if request.method == 'POST':
        form = LotteryDrawForm(request.POST, instance=draw)
        if form.is_valid():
            form.save()
            messages.success(request, f'Draw {draw.draw_date} updated.')
            return redirect('draw_list')
    else:
        form = LotteryDrawForm(instance=draw)
    return render(request, 'analysis/draw_form.html', {'form': form, 'action': 'Edit', 'draw': draw})


@require_POST
def draw_delete(request, pk):
    draw = get_object_or_404(LotteryDraw, pk=pk)
    draw.delete()
    messages.success(request, 'Draw deleted.')
    if request.htmx:
        return HttpResponse('')   # HTMX removes the row
    return redirect('draw_list')


# ============================================================
# Analysis — Run & Results
# ============================================================
def analysis_run(request):
    """Select draw + lottery type and kick off the analysis."""
    draws = LotteryDraw.objects.all()
    form = AnalysisRunForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        lottery_type = form.cleaned_data['lottery_type']
        history_limit = form.cleaned_data['history_limit']
        target_date = form.cleaned_data.get('target_draw_date')
        coverage_budget = form.cleaned_data.get('coverage_budget') or 10

        # The reference draw is the latest one (or any they pick)
        reference_draw_id = request.POST.get('reference_draw_id')
        if reference_draw_id:
            ref_draw = get_object_or_404(LotteryDraw, pk=reference_draw_id)
        else:
            ref_draw = LotteryDraw.objects.first()
            if not ref_draw:
                messages.error(request, 'Please add at least one lottery draw first.')
                return redirect('draw_add')

        # Pull historical numbers up to (and including) the reference draw
        all_draws = LotteryDraw.objects.filter(
            draw_date__lte=ref_draw.draw_date
        ).order_by('draw_date')[:history_limit]

        numbers = []
        dates = []
        for d in all_draws:
            raw = d.get_number_for_type(lottery_type)
            if raw and raw.isdigit():
                numbers.append(int(raw))
                dates.append(datetime.combine(d.draw_date, datetime.min.time()))

        if len(numbers) < 3:
            messages.warning(request, 'Not enough historical data (minimum 3 draws). Please add more draws.')
            return render(request, 'analysis/analysis_run.html', {
                'form': form, 'draws': draws
            })

        # Load formula configs
        formula_configs = FormulaConfig.objects.all()
        active_codes = {fc.formula_code for fc in formula_configs if fc.is_active}
        weights = {fc.formula_code: fc.weight for fc in formula_configs}

        # Run the engine
        num_digits = 2 if lottery_type == '2D' else 3
        space = 10 ** num_digits
        top_n = max(1, min(coverage_budget, space))
        engine = FormulaEngine(numbers=numbers, dates=dates, num_digits=num_digits)
        formula_results = engine.run_all(active_codes=active_codes, weights=weights)

        option_a = engine.aggregate_option_a(formula_results, top_n)
        option_b = engine.aggregate_option_b(formula_results, top_n)
        # Option C is now the honest coverage set sized to the chosen budget.
        option_c = engine.aggregate_coverage(formula_results, top_n, num_digits)

        # Persist the session
        session = AnalysisSession.objects.create(
            reference_draw=ref_draw,
            lottery_type=lottery_type,
            target_draw_date=target_date,
            history_limit=len(numbers),
            formulas_run=len(formula_results),
            formulas_active=len(active_codes),
            formula_raw_results={k: v[:10] for k, v in formula_results.items()},
            option_a_results=option_a,
            option_b_results=option_b,
            option_c_results=option_c,
        )

        # Save individual prediction entries
        for rank, (num_str, count) in enumerate(option_a, 1):
            PredictionEntry.objects.create(
                session=session, option='A', rank=rank,
                number=num_str, frequency_count=int(count),
            )
        for rank, (num_str, score) in enumerate(option_b, 1):
            PredictionEntry.objects.create(
                session=session, option='B', rank=rank,
                number=num_str, ranking_score=float(score),
            )
        for rank, (num_str, score) in enumerate(option_c, 1):
            PredictionEntry.objects.create(
                session=session, option='C', rank=rank,
                number=num_str, ranking_score=float(score),
            )

        return redirect('analysis_detail', pk=session.pk)

    return render(request, 'analysis/analysis_run.html', {'form': form, 'draws': draws})


def analysis_detail(request, pk):
    session = get_object_or_404(AnalysisSession, pk=pk)
    predictions_a = session.predictions.filter(option='A').order_by('rank')
    predictions_b = session.predictions.filter(option='B').order_by('rank')
    predictions_c = session.predictions.filter(option='C').order_by('rank')

    # Formula breakdown table (top-5 slice of each formula)
    formula_breakdown = []
    configs = {fc.formula_code: fc for fc in FormulaConfig.objects.all()}
    for code, results in session.formula_raw_results.items():
        cfg = configs.get(code)
        formula_breakdown.append({
            'code': code,
            'name': cfg.formula_name if cfg else code,
            'group': cfg.formula_group if cfg else '—',
            'top5': results[:5],
        })
    formula_breakdown.sort(key=lambda x: x['code'])

    # Honest expectation: covering N numbers out of the whole space.
    num_digits = 2 if session.lottery_type == '2D' else 3
    space = 10 ** num_digits
    covered = predictions_c.count() or predictions_a.count()
    coverage_pct = round(covered / space * 100, 2) if covered else 0

    return render(request, 'analysis/analysis_detail.html', {
        'session': session,
        'predictions_a': predictions_a,
        'predictions_b': predictions_b,
        'predictions_c': predictions_c,
        'formula_breakdown': formula_breakdown,
        'coverage_count': covered,
        'coverage_space': space,
        'coverage_pct': coverage_pct,
    })


def analysis_history(request):
    sessions = AnalysisSession.objects.select_related('reference_draw').all()
    return render(request, 'analysis/analysis_history.html', {'sessions': sessions})


# ============================================================
# Generate 6-Digit Numbers
# ============================================================
def generate_six_digits(request, session_pk, number, option):
    """Generate all possible 6-digit combinations from a predicted number."""
    session = get_object_or_404(AnalysisSession, pk=session_pk)
    lottery_type = session.lottery_type

    # Generate combinations based on lottery type
    if lottery_type == '2D':
        # 2D = last 2 digits → need to generate first 4 digits
        # Examples: 0000**23**, 0001**23**, ..., 9999**23**
        combinations = [f"{i:04d}{number}" for i in range(10000)]
    elif lottery_type == '3F':
        # 3F = first 3 digits → need to generate last 3 digits
        # Examples: **123**000, **123**001, ..., **123**999
        combinations = [f"{number}{i:03d}" for i in range(1000)]
    elif lottery_type == '3B':
        # 3B = last 3 digits → need to generate first 3 digits
        # Examples: 000**456**, 001**456**, ..., 999**456**
        combinations = [f"{i:03d}{number}" for i in range(1000)]
    else:
        combinations = []

    return render(request, 'analysis/generate_six_digits.html', {
        'session': session,
        'number': number,
        'option': option,
        'lottery_type': lottery_type,
        'combinations': combinations,
        'count': len(combinations),
    })


# ============================================================
# Checklist — Verify Predictions
# ============================================================
def checklist(request):
    """Show unverified sessions alongside available draws for verification."""
    unverified = AnalysisSession.objects.filter(
        predictions__is_verified=False
    ).distinct().select_related('reference_draw').order_by('-created_at')

    verified = PredictionEntry.objects.filter(
        is_verified=True
    ).select_related('session', 'verified_against').order_by('-verified_at')[:30]

    draws = LotteryDraw.objects.all()

    return render(request, 'analysis/checklist.html', {
        'unverified': unverified,
        'verified': verified,
        'draws': draws,
    })


@require_POST
def verify_session(request, session_pk):
    """Mark all predictions in a session as verified against a chosen draw."""
    session = get_object_or_404(AnalysisSession, pk=session_pk)
    actual_draw_id = request.POST.get('actual_draw_id')
    actual_draw = get_object_or_404(LotteryDraw, pk=actual_draw_id)

    for pred in session.predictions.all():
        pred.verify(actual_draw)

    # Self-learning: adjust formula weights based on which formulas predicted correctly
    actual_number = actual_draw.get_number_for_type(session.lottery_type)
    if actual_number and session.formula_raw_results:
        formula_configs = {fc.formula_code: fc for fc in FormulaConfig.objects.all()}
        to_update = []
        for code, results in session.formula_raw_results.items():
            top5_numbers = [r[0] for r in results[:5]]
            fc = formula_configs.get(code)
            if fc:
                if actual_number in top5_numbers:
                    fc.weight = min(3.0, round(fc.weight + 0.15, 2))
                else:
                    fc.weight = max(0.1, round(fc.weight - 0.05, 2))
                to_update.append(fc)
        FormulaConfig.objects.bulk_update(to_update, ['weight'])

    messages.success(request, f'Session verified against draw {actual_draw.draw_date}.')
    if request.htmx:
        # Return partial — summary row
        predictions_a = session.predictions.filter(option='A').order_by('rank')
        predictions_b = session.predictions.filter(option='B').order_by('rank')
        return render(request, 'analysis/partials/verified_row.html', {
            'session': session,
            'predictions_a': predictions_a,
            'predictions_b': predictions_b,
            'actual_draw': actual_draw,
        })
    return redirect('checklist')


# ============================================================
# Formula Settings
# ============================================================
def formula_settings(request):
    configs = FormulaConfig.objects.all()

    if request.method == 'POST':
        for cfg in configs:
            weight_key = f'weight_{cfg.formula_code}'
            active_key = f'active_{cfg.formula_code}'
            try:
                cfg.weight = float(request.POST.get(weight_key, 1.0))
                cfg.is_active = active_key in request.POST
                cfg.save()
            except (ValueError, TypeError):
                pass
        messages.success(request, 'Formula settings saved.')
        if request.htmx:
            return HttpResponse('<div class="toast-success px-4 py-2">Settings saved!</div>')
        return redirect('formula_settings')

    groups = {}
    for cfg in configs:
        groups.setdefault(cfg.formula_group, []).append(cfg)

    return render(request, 'analysis/formula_settings.html', {
        'groups': groups,
        'total': configs.count(),
        'active': configs.filter(is_active=True).count(),
    })


# ============================================================
# Combine 3F + 3B → 6-Digit First Prize Candidates
# ============================================================
def combine_6d(request):
    """
    Cross-join top-N predictions from a 3F session and a 3B session
    to produce 6-digit first-prize candidates.
    """
    sessions_3f = (AnalysisSession.objects
                   .filter(lottery_type='3F')
                   .select_related('reference_draw')
                   .order_by('-created_at')[:30])
    sessions_3b = (AnalysisSession.objects
                   .filter(lottery_type='3B')
                   .select_related('reference_draw')
                   .order_by('-created_at')[:30])

    front_session_pk = request.POST.get('front_session') or request.GET.get('front_session')
    back_session_pk  = request.POST.get('back_session')  or request.GET.get('back_session')

    try:
        top_n = max(1, min(int(request.POST.get('top_n', 5)), 10))
    except (ValueError, TypeError):
        top_n = 5

    front_session = back_session = None
    front_numbers = back_numbers = []
    combinations  = []

    if front_session_pk:
        front_session = AnalysisSession.objects.filter(
            pk=front_session_pk, lottery_type='3F'
        ).select_related('reference_draw').first()

    if back_session_pk:
        back_session = AnalysisSession.objects.filter(
            pk=back_session_pk, lottery_type='3B'
        ).select_related('reference_draw').first()

    if request.method == 'POST' and front_session and back_session:
        def _top_numbers(session, n):
            # Prefer Option C (enhanced consensus), then A
            for opt in ('C', 'A', 'B'):
                qs = session.predictions.filter(option=opt).order_by('rank')[:n]
                if qs.exists():
                    return [p.number for p in qs]
            return []

        front_numbers = _top_numbers(front_session, top_n)
        back_numbers  = _top_numbers(back_session,  top_n)
        combinations  = [f + b for f in front_numbers for b in back_numbers]

    return render(request, 'analysis/combine_6d.html', {
        'sessions_3f':    sessions_3f,
        'sessions_3b':    sessions_3b,
        'front_session':  front_session,
        'back_session':   back_session,
        'front_numbers':  front_numbers,
        'back_numbers':   back_numbers,
        'combinations':   combinations,
        'top_n':          top_n,
        'total':          len(combinations),
    })


# ============================================================
# HTMX Partials
# ============================================================
def partial_formula_table(request, session_pk):
    """HTMX partial: formula breakdown table for a session."""
    session = get_object_or_404(AnalysisSession, pk=session_pk)
    configs = {fc.formula_code: fc for fc in FormulaConfig.objects.all()}
    rows = []
    for code, results in session.formula_raw_results.items():
        cfg = configs.get(code)
        rows.append({
            'code': code,
            'name': cfg.formula_name if cfg else code,
            'group': cfg.formula_group if cfg else '—',
            'top5': results[:5],
        })
    rows.sort(key=lambda x: x['code'])
    return render(request, 'analysis/partials/formula_table.html', {
        'formula_breakdown': rows,
    })

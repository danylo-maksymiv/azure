from django.shortcuts import render, redirect
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status, permissions
from .forms import AddressForm, ValidatorForm, BlockForm, TransactionForm, TransactionDataForm, ContractForm, ContractDataForm, TokenForm, MempoolForm
from .serializers import *
from .repositories import Repository
from .repositories.validator_repository import ValidatorRepository
from django.db.models.deletion import RestrictedError
from django.contrib.auth.decorators import login_required
import plotly.express as px
from django.shortcuts import render
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.models import ColumnDataSource, FactorRange
from bokeh.transform import dodge
from bokeh.palettes import Category20,Category10
import pandas as pd
import decimal
from bokeh.models import ColumnDataSource, HoverTool
from bokeh.palettes import viridis
import numpy as np
from bokeh.transform import cumsum
from math import pi
import plotly.graph_objects as go

def plotly_interactive_difficulty(request):
    # Отримуємо дані про блоки
    blocks = Repository.block().get_all()
    diff_df = pd.DataFrame(blocks.values('status', 'difficulty'))

    if diff_df.empty:
        return render(request, "graphs/plotly_graph.html", {"error": "No data available for interactive graph."})

    # Агрегація середньої складності за статусом
    diff_agg = diff_df.groupby('status', as_index=False)['difficulty'].mean()
    diff_agg['difficulty'] = diff_agg['difficulty'].astype(float)

    # Створюємо інтерактивний графік за допомогою Plotly
    fig = px.bar(
        diff_agg,
        x='status',
        y='difficulty',
        title="Середня складність за статусом блоку (інтерактивно)",
        labels={'status': 'Статус блоку', 'difficulty': 'Середня складність'},
        hover_data=['status', 'difficulty']
    )

    # Налаштування макета
    fig.update_layout(
        xaxis_title="Статус блоку",
        yaxis_title="Середня складність",
        showlegend=False
    )

    # Перетворюємо графік у HTML
    graph_html = fig.to_html(full_html=False)

    return render(request, "graphs/plotly_graph.html", {"graph_html": graph_html})


def bokeh_interactive_difficulty(request):
    # Отримуємо дані про блоки
    blocks = Repository.block().get_all()
    if not blocks.exists():
        return render(request, "graphs/bokeh_graph.html", {"error": "No data available."})

    # Перетворюємо QuerySet у DataFrame
    diff_df = pd.DataFrame(blocks.values('status', 'difficulty'))
    if diff_df.empty:
        return render(request, "graphs/bokeh_graph.html", {"error": "No data available."})

    # Агрегація середньої складності за статусом
    diff_agg = diff_df.groupby('status', as_index=False)['difficulty'].mean()

    # Конвертуємо decimal.Decimal у float
    diff_agg['difficulty'] = diff_agg['difficulty'].astype(float)

    # Створюємо ColumnDataSource для Bokeh
    source = ColumnDataSource(diff_agg)

    # Створюємо фігуру
    p = figure(x_range=diff_agg['status'].astype(str), height=500, width=600,
               title="Середня складність за статусом блоку (інтерактивно)",
               toolbar_location=None, tools="")

    # Додаємо стовпчики
    r = p.vbar(x='status', top='difficulty', source=source, width=0.9, color='blue')

    # Додаємо HoverTool для відображення інформації при наведенні
    hover = HoverTool(tooltips=[
        ("Статус", "@status"),
        ("Середня складність", "@difficulty")
    ], renderers=[r])
    p.add_tools(hover)

    p.xaxis.axis_label = "Статус"
    p.yaxis.axis_label = "Середня складність"

    script, div = components(p)
    return render(request, "graphs/bokeh_graph.html", {"interactive_script": script, "interactive_div": div})


def plotly_reward_status_pie(request):
    reward_data = ValidatorRepository.validator_block_statistics()
    df = pd.DataFrame(reward_data)
    if df.empty:
        return render(request, "graphs/plotly_graph.html", {"error": "No data available."})

    agg_df = df.groupby('status', as_index=False)['total_reward'].sum()
    fig = px.pie(agg_df, names='status', values='total_reward', title="Розподіл сумарної винагороди за статусами")
    graph_html = fig.to_html(full_html=False)
    return render(request, "graphs/plotly_graph.html", {"graph_html": graph_html})


def bokeh_reward_status_pie(request):
    # Отримуємо дані про винагороди валідаторів
    reward_data = ValidatorRepository.validator_block_statistics()
    df = pd.DataFrame(reward_data)

    if df.empty:
        return render(request, "graphs/bokeh_graph.html", {"error": "No data available."})

    # Перевіряємо наявність необхідних колонок
    required_columns = {'status', 'total_reward'}
    if not required_columns.issubset(df.columns):
        return render(request, "graphs/bokeh_graph.html", {"error": "Missing required data fields."})

    # Агрегація сумарної винагороди за статусом
    agg_df = df.groupby('status', as_index=False)['total_reward'].sum()

    if agg_df.empty:
        return render(request, "graphs/bokeh_graph.html", {"error": "No aggregated data available."})

    # Конвертуємо 'total_reward' у float для уникнення TypeError
    try:
        agg_df['total_reward'] = agg_df['total_reward'].astype(float)
    except (ValueError, TypeError) as e:
        print(f"Error converting 'total_reward' to float: {e}")
        return render(request, "graphs/bokeh_graph.html", {"error": "Invalid data format for 'total_reward'."})

    # Обчислення кутів для pie chart
    agg_df['angle'] = agg_df['total_reward'] / agg_df['total_reward'].sum() * 2 * pi

    # Призначення кольорів
    agg_df['color'] = viridis(len(agg_df))

    # Створення ColumnDataSource
    source = ColumnDataSource(agg_df)

    # Побудова pie chart за допомогою Bokeh
    p = figure(
        height=500,
        width=500,
        title="Розподіл сумарної винагороди за статусами",
        toolbar_location=None,
        tools=""
    )

    p.wedge(
        x=0,
        y=0,
        radius=0.4,
        start_angle=cumsum('angle', include_zero=True),
        end_angle=cumsum('angle'),
        line_color="white",
        fill_color='color',
        legend_field='status',
        source=source
    )

    p.axis.visible = False
    p.grid.visible = False

    # Генерація скрипту та div
    script, div = components(p)

    return render(request, "graphs/bokeh_graph.html", {"script": script, "div": div})

##############################################
# ПАРА 2: Лінійний графік транзакцій за днями (Plotly і Bokeh)
##############################################
def plotly_daily_transactions_line(request):
    transaction_data = ValidatorRepository.validator_transaction_statistics()
    df = pd.DataFrame(transaction_data)
    if df.empty:
        return render(request, "graphs/plotly_graph.html", {"error": "No data available."})

    df['date'] = pd.to_datetime(df['date'])
    daily_agg = df.groupby('date', as_index=False)['transactions'].sum()

    fig = px.line(
        daily_agg,
        x='date',
        y='transactions',
        title="Сумарна кількість транзакцій за днями (лінійний графік)"
    )
    fig.update_xaxes(tickformat="%Y-%m-%d", tickangle=45)
    fig.update_layout(xaxis_title="Дата", yaxis_title="Кількість транзакцій")

    graph_html = fig.to_html(full_html=False)
    return render(request, "graphs/plotly_graph.html", {"graph_html": graph_html})


def bokeh_daily_transactions_line(request):
    transaction_data = ValidatorRepository.validator_transaction_statistics()
    df = pd.DataFrame(transaction_data)
    if df.empty:
        return render(request, "graphs/bokeh_graph.html", {"error": "No data available."})

    df['date'] = pd.to_datetime(df['date'])
    daily_agg = df.groupby('date', as_index=False)['transactions'].sum()

    source = ColumnDataSource(daily_agg)
    p = figure(x_axis_type='datetime', title="Сумарна кількість транзакцій за днями (лінія)", height=500, width=900)
    p.line(x='date', y='transactions', source=source, line_width=2, color='navy')
    p.circle(x='date', y='transactions', source=source, size=6, color='navy', fill_color='white')
    p.xaxis.axis_label = "Дата"
    p.yaxis.axis_label = "Кількість транзакцій"

    script, div = components(p)
    return render(request, "graphs/bokeh_graph.html", {"script": script, "div": div})

##############################################
# ПАРА 3: Скатер-плот для Block (height vs reward)
##############################################
def plotly_block_scatter(request):
    blocks = Repository.block().get_all()
    df = pd.DataFrame(blocks.values('height', 'reward'))
    if df.empty:
        return render(request, "graphs/plotly_graph.html", {"error": "No blocks data available."})

    df['reward'] = df['reward'].apply(lambda x: float(x) if isinstance(x, decimal.Decimal) else x)
    fig = px.scatter(
        df,
        x='height',
        y='reward',
        title="Залежність винагороди від висоти блоку (scatter)",
        labels={'height': 'Висота блоку', 'reward': 'Винагорода'}
    )

    graph_html = fig.to_html(full_html=False)
    return render(request, "graphs/plotly_graph.html", {"graph_html": graph_html})


def bokeh_block_scatter(request):
    blocks = Repository.block().get_all()
    df = pd.DataFrame(blocks.values('height', 'reward'))
    if df.empty:
        return render(request, "graphs/bokeh_graph.html", {"error": "No blocks data available."})

    df['reward'] = df['reward'].apply(lambda x: float(x) if isinstance(x, decimal.Decimal) else x)
    source = ColumnDataSource(df)
    p = figure(title="Залежність винагороди від висоти блоку (scatter)", height=500, width=900)
    p.circle(x='height', y='reward', source=source, size=8, color='green', alpha=0.6)
    p.xaxis.axis_label = "Висота блоку"
    p.yaxis.axis_label = "Винагорода"

    script, div = components(p)
    return render(request, "graphs/bokeh_graph.html", {"script": script, "div": div})

##############################################
# ПАРА 4: Гістограма gas_used з transaction_data
##############################################
def plotly_gas_used_histogram(request):
    all_tx_data = Repository.transaction_data().get_all()
    if not all_tx_data:
        return render(request, "graphs/plotly_graph.html", {"error": "No transaction data available."})

    df = pd.DataFrame(all_tx_data.values('gas_used'))
    if df.empty:
        return render(request, "graphs/plotly_graph.html", {"error": "No transaction data available."})

    fig = px.histogram(
        df,
        x='gas_used',
        nbins=20,
        title="Розподіл gas_used (Histogram)"
    )
    fig.update_layout(xaxis_title="gas_used", yaxis_title="Count")

    graph_html = fig.to_html(full_html=False)
    return render(request, "graphs/plotly_graph.html", {"graph_html": graph_html})


def bokeh_gas_used_histogram(request):
    all_tx_data = Repository.transaction_data().get_all()
    if not all_tx_data:
        return render(request, "graphs/bokeh_graph.html", {"error": "No transaction data available."})

    df = pd.DataFrame(all_tx_data.values('gas_used'))
    if df.empty:
        return render(request, "graphs/bokeh_graph.html", {"error": "No transaction data available."})

    gas_used_values = df['gas_used'].astype(int)
    hist, edges = pd.cut(gas_used_values, bins=20, retbins=True)
    hist_counts = gas_used_values.groupby(hist).count().values

    # Для гістограми Bokeh використовуємо quad
    p = figure(title="Розподіл gas_used (Histogram) Bokeh", width=900, height=500)
    p.quad(top=hist_counts, bottom=0, left=edges[:-1], right=edges[1:], fill_color='red', line_color='white')
    p.xaxis.axis_label = "gas_used"
    p.yaxis.axis_label = "Count"

    script, div = components(p)
    return render(request, "graphs/bokeh_graph.html", {"script": script, "div": div})
def plotly_graph(request):
    data = Repository.validator_block_statistics()
    df = pd.DataFrame(data)

    fig = px.bar(
        df,
        x="address",
        y="total_reward",
        color="status",
        title="Сумарна винагорода валідаторів за статусами блоків",
        labels={"address": "Адреса валідатора", "total_reward": "Сумарна винагорода"},
        barmode="group",
    )

    fig.update_xaxes(tickangle=45)
    fig.update_layout(
        margin=dict(b=100),
        xaxis_title="Адреса валідатора",
        yaxis_title="Сумарна винагорода",
    )

    graph_html = fig.to_html(full_html=False)

    return render(request, "graphs/plotly_graph.html", {"graph_html": graph_html})


def plotly_dashboard(request):
    reward_data = ValidatorRepository.validator_block_statistics()
    transaction_data = ValidatorRepository.validator_transaction_statistics()

    if not reward_data and not transaction_data:
        return render(request, "graphs/plotly_graph.html", {"error": "No data available."})

    reward_df = pd.DataFrame(reward_data)
    reward_fig = px.bar(
        reward_df,
        x="address",
        y="total_reward",
        color="status",
        title="Сумарна винагорода валідаторів за статусами",
        labels={"address": "Адреса валідатора", "total_reward": "Сумарна винагорода"},
        barmode="group",
    )
    reward_fig.update_xaxes(tickangle=45)
    reward_graph_html = reward_fig.to_html(full_html=False)

    # ********** Графік транзакцій (стовпчастий) **********
    transaction_df = pd.DataFrame(transaction_data)
    if not transaction_df.empty:
        transaction_df['date'] = pd.to_datetime(transaction_df['date'])
        transaction_df = transaction_df.sort_values(by='date')
        transaction_fig = px.bar(
            transaction_df,
            x='date',
            y='transactions',
            color='address',
            title="Кількість транзакцій валідаторів по днях",
            labels={'date': 'Дата', 'transactions': 'Кількість транзакцій', 'address': 'Валідатор'},
            barmode='group',
        )
        transaction_fig.update_xaxes(tickformat="%Y-%m-%d", tickangle=45)
        transaction_graph_html = transaction_fig.to_html(full_html=False)
    else:
        transaction_graph_html = "<p>Дані про транзакції відсутні.</p>"

    # ********** Пай-чарт винагород **********
    agg_df = reward_df.groupby('status', as_index=False)['total_reward'].sum()
    if agg_df.empty:
        mock_data = pd.DataFrame({
            'status': ['No Data'],
            'total_reward': [0]
        })
        pie_fig = px.pie(mock_data, names='status', values='total_reward', title="Розподіл сумарної винагороди (No Data)")
    else:
        pie_fig = px.pie(agg_df, names='status', values='total_reward', title="Розподіл сумарної винагороди за статусами")
    pie_graph_html = pie_fig.to_html(full_html=False)

    blocks = Repository.block().get_all()
    block_df = pd.DataFrame(blocks.values('height', 'reward'))
    if block_df.empty:
        scatter_graph_html = "<p>Немає даних про блоки для скатер-графіка</p>"
    else:
        block_df['reward'] = block_df['reward'].apply(lambda x: float(x) if isinstance(x, decimal.Decimal) else x)
        scatter_fig = px.scatter(block_df, x='height', y='reward', title="Залежність винагороди від висоти блоку")
        scatter_graph_html = scatter_fig.to_html(full_html=False)

    all_tx_data = Repository.transaction_data().get_all()
    if not all_tx_data:
        histogram_graph_html = "<p>Немає даних для гістограми gas_used</p>"
    else:
        gas_df = pd.DataFrame(all_tx_data.values('gas_used'))
        if gas_df.empty:
            histogram_graph_html = "<p>Немає даних для гістограми gas_used</p>"
        else:
            hist_fig = px.histogram(gas_df, x='gas_used', nbins=20, title="Розподіл gas_used (Histogram)")
            histogram_graph_html = hist_fig.to_html(full_html=False)

    # ********** Агрегований графік (Середня складність за статусом блоку) **********
    diff_df = pd.DataFrame(blocks.values('status', 'difficulty'))
    if diff_df.empty:
        aggregator_graph_html = "<p>Немає даних для агрегованої статистики складності.</p>"
    else:
        diff_agg = diff_df.groupby('status', as_index=False)['difficulty'].mean()
        aggregator_fig = px.bar(
            diff_agg,
            x='status',
            y='difficulty',
            title="Середня складність за статусом блоку",
            labels={"difficulty": "Середня складність", "status": "Статус блоку"}
        )
        aggregator_graph_html = aggregator_fig.to_html(full_html=False)

    # ********** Інтерактивний графік: Середня складність за статусом блоку **********
    if not diff_df.empty:
        statuses_diff = diff_agg['status'].unique()
        interactive_fig = go.Figure()

        for status in statuses_diff:
            subset = diff_agg[diff_agg['status'] == status]
            interactive_fig.add_trace(go.Bar(
                x=subset['status'],
                y=subset['difficulty'],
                name=status
            ))

        buttons = [
            dict(
                label="Всі статуси",
                method="update",
                args=[{"visible": [True] * len(statuses_diff)},
                      {"title": "Середня складність за статусом блоку"}]
            )
        ]

        for i, status in enumerate(statuses_diff):
            visibility = [False] * len(statuses_diff)
            visibility[i] = True
            buttons.append(dict(
                label=status,
                method="update",
                args=[{"visible": visibility},
                      {"title": f"Середня складність за статусом блоку: {status}"}]
            ))

        interactive_fig.update_layout(
            updatemenus=[
                dict(
                    type="buttons",
                    direction="left",
                    buttons=buttons,
                    pad={"r": 10, "t": 10},
                    showactive=True,
                    x=0.0,
                    xanchor="left",
                    y=1.15,
                    yanchor="top"
                )
            ]
        )

        interactive_fig.update_layout(
            xaxis_title="Статус блоку",
            yaxis_title="Середня складність",
            showlegend=True
        )

        interactive_graph_html = interactive_fig.to_html(full_html=False)
    else:
        interactive_graph_html = "<p>Немає даних для інтерактивного графіка.</p>"

    return render(request, "graphs/plotly_graph.html", {
        "reward_graph_html": reward_graph_html,
        "transaction_graph_html": transaction_graph_html,
        "pie_graph_html": pie_graph_html,
        "scatter_graph_html": scatter_graph_html,
        "histogram_graph_html": histogram_graph_html,
        "aggregator_graph_html": aggregator_graph_html,
        "interactive_graph_html": interactive_graph_html,
    })



@login_required
def bokeh_dashboard(request):
    reward_data = ValidatorRepository.validator_block_statistics()
    transaction_data = ValidatorRepository.validator_transaction_statistics()

    if not reward_data and not transaction_data:
        return render(request, "graphs/bokeh_graph.html", {"error": "No data available."})

    reward_script, reward_div = None, None
    transaction_script, transaction_div = None, None
    pie_script, pie_div = None, None
    scatter_script, scatter_div = None, None
    hist_script, hist_div = None, None
    aggregator_script, aggregator_div = None, None

    ##############################################
    # 1: Графік винагород (Bar Chart)
    ##############################################
    try:
        reward_df = pd.DataFrame(reward_data)
        if reward_df.empty or 'address' not in reward_df.columns or 'total_reward' not in reward_df.columns:
            reward_div = "<p>Немає даних для графіка винагород.</p>"
        else:
            reward_df['total_reward'] = reward_df['total_reward'].astype(float)

            addresses = sorted(reward_df['address'].unique())
            statuses = sorted(reward_df['status'].unique())

            palette = viridis(len(statuses))

            data = {'address': addresses}
            for status in statuses:
                status_data = reward_df[reward_df['status'] == status].set_index('address')['total_reward'].reindex(
                    addresses, fill_value=0).tolist()
                data[status] = status_data
            source = ColumnDataSource(data=data)

            p = figure(
                x_range=addresses,
                height=500,
                width=900,
                title="Сумарна винагорода валідаторів за статусами",
                toolbar_location=None,
                tools=""
            )

            num_statuses = len(statuses)
            bar_width = 0.8 / num_statuses
            for i, status in enumerate(statuses):
                p.vbar(
                    x=dodge('address', -0.4 + i * bar_width, range=p.x_range),
                    top=status,
                    width=bar_width * 0.9,
                    source=source,
                    color=palette[i],
                    legend_label=status
                )

            p.x_range.range_padding = 0.05
            p.xgrid.grid_line_color = None
            p.y_range.start = 0
            p.xaxis.major_label_orientation = 1.2
            p.xaxis.axis_label = "Адреса валідатора"
            p.yaxis.axis_label = "Сумарна винагорода"
            p.legend.location = "top_left"
            p.legend.orientation = "horizontal"

            reward_script, reward_div = components(p)
    except Exception as e:
        print(f"Error in reward graph: {e}")
        reward_div = f"<p>Помилка при побудові графіка винагород: {e}</p>"

    ##############################################
    # 2: Графік транзакцій (Bar Chart by Days)
    ##############################################
    try:
        transaction_df = pd.DataFrame(transaction_data)
        if transaction_df.empty:
            transaction_div = "<p>Дані про транзакції відсутні.</p>"
        else:
            required_fields = {'date', 'transactions', 'address'}
            if not required_fields.issubset(transaction_df.columns):
                transaction_div = "<p>Немає необхідних полів для графіка транзакцій.</p>"
            else:
                transaction_df['date'] = pd.to_datetime(transaction_df['date'], errors='coerce')
                transaction_df = transaction_df.dropna(subset=['date']).sort_values(by='date').reset_index(drop=True)

                transaction_p = figure(
                    x_axis_type="datetime",
                    title="Кількість транзакцій валідаторів по днях",
                    width=900,
                    height=500,
                    toolbar_location=None,
                    tools=""
                )

                unique_addresses = transaction_df['address'].unique()
                colors = viridis(len(unique_addresses)) if len(unique_addresses) <= len(viridis(256)) else Category20[20]

                for i, addr in enumerate(unique_addresses):
                    addr_data = transaction_df[transaction_df['address'] == addr]
                    source = ColumnDataSource(addr_data)
                    transaction_p.vbar(
                        x='date',
                        top='transactions',
                        width=0.8,
                        source=source,
                        color=colors[i % len(colors)],
                        legend_label=str(addr)
                    )

                transaction_p.xaxis.axis_label = "Дата"
                transaction_p.yaxis.axis_label = "Кількість транзакцій"
                transaction_p.xgrid.grid_line_color = None
                transaction_p.y_range.start = 0
                transaction_p.legend.location = "top_left"
                transaction_p.legend.orientation = "vertical"

                transaction_script, transaction_div = components(transaction_p)
    except Exception as e:
        print(f"Error in transaction graph: {e}")
        transaction_div = "<p>Помилка при побудові графіка транзакцій.</p>"

    ##############################################
    # 3: Пай-чарт винагород
    ##############################################
    try:
        if not reward_df.empty and 'status' in reward_df.columns and 'total_reward' in reward_df.columns:
            agg_df = reward_df.groupby('status', as_index=False)['total_reward'].sum()
            if agg_df.empty:
                pie_div = "<p>Немає даних для пай-чарту.</p>"
                pie_script = ""
            else:
                agg_df['total_reward'] = agg_df['total_reward'].astype(float)

                agg_df['angle'] = agg_df['total_reward'] / agg_df['total_reward'].sum() * 2 * pi
                agg_df['color'] = viridis(len(agg_df))

                source_pie = ColumnDataSource(agg_df)

                pie_p = figure(
                    height=500,
                    width=500,
                    title="Розподіл сумарної винагороди за статусами",
                    toolbar_location=None,
                    tools=""
                )

                pie_p.wedge(
                    x=0,
                    y=0,
                    radius=0.4,
                    start_angle=cumsum('angle', include_zero=True),
                    end_angle=cumsum('angle'),
                    line_color="white",
                    fill_color='color',
                    legend_field='status',
                    source=source_pie
                )

                pie_p.axis.visible = False
                pie_p.grid.visible = False
                pie_p.legend.location = "top_left"
                pie_p.legend.orientation = "horizontal"

                pie_script, pie_div = components(pie_p)
        else:
            pie_div = "<p>Немає даних для пай-чарту.</p>"
            pie_script = ""
    except Exception as e:
        print(f"Error in pie chart: {e}")
        pie_div = "<p>Помилка при побудові пай-чарту.</p>"
        pie_script = ""

    ##############################################
    # 4: Scatter-графік (Height vs Reward)
    ##############################################
    try:
        blocks = Repository.block().get_all()
        block_df = pd.DataFrame(blocks.values('height', 'reward'))
        if block_df.empty:
            scatter_div = "<p>Немає даних про блоки для скатер-графіка</p>"
            scatter_script = ""
        else:
            block_df['reward'] = block_df['reward'].astype(float)

            source_scatter = ColumnDataSource(block_df)

            scatter_p = figure(
                title="Залежність винагороди від висоти блоку (scatter)",
                height=500,
                width=900,
                toolbar_location=None,
                tools=""
            )

            scatter_p.circle(x='height', y='reward', source=source_scatter, size=8, color='green', alpha=0.6)

            scatter_p.xaxis.axis_label = "Висота блоку"
            scatter_p.yaxis.axis_label = "Винагорода"

            scatter_script, scatter_div = components(scatter_p)
    except Exception as e:
        print(f"Error in scatter chart: {e}")
        scatter_div = "<p>Помилка при побудові скатер-графіка.</p>"
        scatter_script = ""

    ##############################################
    # 5: Гістограма gas_used
    ##############################################
    try:
        all_tx_data = Repository.transaction_data().get_all()
        if not all_tx_data:
            hist_div = "<p>Немає даних для гістограми gas_used</p>"
            hist_script = ""
        else:
            gas_df = pd.DataFrame(all_tx_data.values('gas_used'))
            if gas_df.empty:
                hist_div = "<p>Немає даних для гістограми gas_used</p>"
                hist_script = ""
            else:
                gas_df['gas_used'] = gas_df['gas_used'].astype(int)
                hist_values, edges = np.histogram(gas_df['gas_used'], bins=20)

                hist_source = ColumnDataSource(data=dict(
                    top=hist_values,
                    left=edges[:-1],
                    right=edges[1:]
                ))

                hist_p = figure(
                    title="Розподіл gas_used (Histogram)",
                    width=900,
                    height=500,
                    toolbar_location=None,
                    tools=""
                )

                hist_p.quad(
                    top='top',
                    bottom=0,
                    left='left',
                    right='right',
                    fill_color='red',
                    line_color='white',
                    source=hist_source
                )

                hist_p.xaxis.axis_label = "gas_used"
                hist_p.yaxis.axis_label = "Count"

                hist_script, hist_div = components(hist_p)
    except Exception as e:
        print(f"Error in histogram chart: {e}")
        hist_div = "<p>Помилка при побудові гістограми gas_used.</p>"
        hist_script = ""

    ##############################################
    # 6: Агрегований графік (Середня складність за статусом)
    ##############################################
    try:
        blocks = Repository.block().get_all()
        diff_df = pd.DataFrame(blocks.values('status', 'difficulty'))
        if diff_df.empty:
            aggregator_div = "<p>Немає даних для агрегованої статистики складності.</p>"
            aggregator_script = ""
        else:
            diff_agg = diff_df.groupby('status', as_index=False)['difficulty'].mean()
            diff_agg['difficulty'] = diff_agg['difficulty'].astype(float)

            source_agg = ColumnDataSource(diff_agg)

            agg_p = figure(
                x_range=diff_agg['status'].astype(str),
                height=500,
                width=900,
                title="Середня складність за статусом блоку",
                toolbar_location=None,
                tools=""
            )

            agg_p.vbar(
                x='status',
                top='difficulty',
                source=source_agg,
                width=0.9,
                color="purple",
                legend_label="Середня складність"
            )

            agg_p.x_range.range_padding = 0.05
            agg_p.xgrid.grid_line_color = None
            agg_p.y_range.start = 0
            agg_p.xaxis.major_label_orientation = 1.2
            agg_p.xaxis.axis_label = "Статус блоку"
            agg_p.yaxis.axis_label = "Середня складність"
            agg_p.legend.location = "top_left"
            agg_p.legend.orientation = "horizontal"

            aggregator_script, aggregator_div = components(agg_p)
    except Exception as e:
        print(f"Error in aggregator chart: {e}")
        aggregator_div = "<p>Помилка при побудові агрегованого графіка.</p>"
        aggregator_script = ""



    ##############################################
    # Повернення всіх графіків у шаблон
    ##############################################
    return render(request, "graphs/bokeh_graph.html", {
        "reward_script": reward_script, "reward_div": reward_div,
        "transaction_script": transaction_script, "transaction_div": transaction_div,
        "pie_script": pie_script, "pie_div": pie_div,
        "scatter_script": scatter_script, "scatter_div": scatter_div,
        "hist_script": hist_script, "hist_div": hist_div,
        "aggregator_script": aggregator_script, "aggregator_div": aggregator_div,
    })







def bokeh_graph(request):
    # Get data from the repository
    data = Repository.validator_block_statistics()
    df = pd.DataFrame(data)

    # Check if DataFrame is empty
    if df.empty:
        return render(request, 'graphs/bokeh_graph.html', {'error': 'No data available to display.'})

    # Convert decimal.Decimal to float
    df['total_reward'] = df['total_reward'].astype(float)

    # Prepare data for Bokeh
    pivot_df = df.pivot(index='address', columns='status', values='total_reward').fillna(0)

    # Ensure all data is float
    pivot_df = pivot_df.astype(float)

    # Get the list of validators and statuses
    validators = pivot_df.index.tolist()
    statuses = pivot_df.columns.tolist()

    # Prepare data source
    data_dict = {'validators': validators}
    for status in statuses:
        data_dict[status] = pivot_df[status].tolist()

    source = ColumnDataSource(data=data_dict)

    # Create the figure
    p = figure(
        x_range=FactorRange(*validators),
        height=400,
        width=800,
        title="Сумарна винагорода валідаторів за статусами блоків",
        toolbar_location=None,
        tools=""
    )

    # Determine the offsets for grouped bars
    num_statuses = len(statuses)
    bar_width = 0.8 / num_statuses
    offsets = [(-0.4 + bar_width / 2) + i * bar_width for i in range(num_statuses)]

    # Use a color palette
    colors = Category20[max(3, num_statuses)]  # Ensure the palette is large enough

    # Add bars for each status
    for i, status in enumerate(statuses):
        p.vbar(
            x=dodge('validators', offsets[i], range=p.x_range),
            top=status,
            width=bar_width * 0.9,
            source=source,
            color=colors[i % len(colors)],
            legend_label=str(status)
        )

    # Adjust plot aesthetics
    p.x_range.range_padding = 0.05
    p.xgrid.grid_line_color = None
    p.y_range.start = 0
    p.xaxis.major_label_orientation = 1.2  # Rotate x-axis labels if needed
    p.legend.location = "top_left"
    p.legend.orientation = "horizontal"
    p.xaxis.axis_label = "Адреса валідатора"
    p.yaxis.axis_label = "Сумарна винагорода"

    # Generate the script and div components
    script, div = components(p)

    # Pass them to the template
    return render(request, 'graphs/bokeh_graph.html', {'script': script, 'div': div})

def plotly_transactions_per_day(request):
    # Дані про транзакції валідаторів за днями
    data = ValidatorRepository.validator_transaction_statistics()
    df = pd.DataFrame(data)

    if df.empty:
        return render(request, 'graphs/plotly_graph.html', {'error': 'No transaction data available.'})

    # Перетворення стовпців
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values(by='date')

    # Груповий стовпчастий графік
    fig = px.bar(
        df,
        x='date',
        y='transactions',
        color='address',  # Заміна на "address"
        title="Кількість транзакцій валідаторів по днях",
        labels={'date': 'Дата', 'transactions': 'Кількість транзакцій', 'address': 'Валідатор'},
        barmode='group',
    )

    # Оновлення осей і стилю
    fig.update_xaxes(tickformat="%Y-%m-%d", tickangle=45)
    fig.update_layout(
        xaxis_title="Дата",
        yaxis_title="Кількість транзакцій",
        margin=dict(l=40, r=40, t=40, b=120),
    )

    # Перетворюємо графік у HTML
    graph_html = fig.to_html(full_html=False)

    return render(request, "graphs/plotly_graph.html", {"graph_html": graph_html})


def bokeh_transactions_per_day(request):
    # Дані про транзакції валідаторів за днями
    data = ValidatorRepository.validator_transaction_statistics()
    df = pd.DataFrame(data)

    if df.empty:
        return render(request, 'graphs/bokeh_graph.html', {'error': 'No transaction data available.'})

    # Перетворення стовпців
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values(by='date')

    # Перетворення даних у формат Bokeh
    source = ColumnDataSource(df)

    # Груповий графік з датами
    p = figure(
        x_axis_type="datetime",
        title="Кількість транзакцій валідаторів по днях",
        width=900,
        height=500,
        toolbar_location=None
    )

    # Додаємо стовпчики для кожного валідатора
    colors = Category20[len(df['address'].unique())]
    for i, validator in enumerate(df['address'].unique()):  # Заміна на 'address'
        validator_data = df[df['address'] == validator]  # Заміна на 'address'
        source = ColumnDataSource(validator_data)

        p.vbar(
            x='date',
            top='transactions',
            width=0.9,
            source=source,
            legend_label=f"Валідатор: {validator}",
            color=colors[i % len(colors)]
        )

    # Налаштування графіка
    p.xaxis.axis_label = "Дата"
    p.yaxis.axis_label = "Кількість транзакцій"
    p.xgrid.grid_line_color = None
    p.y_range.start = 0
    p.legend.location = "top_left"

    # Генерація компонентів
    script, div = components(p)

    return render(request, 'graphs/bokeh_graph.html', {'script': script, 'div': div})


@login_required
def create(request):
    return render(request, 'create.html')

def get_by(request):
    return render(request, 'get_by.html')

def get_all(request):
    return render(request, 'get_all.html')

def home(request):
    return render(request, 'home.html')

@login_required
def create_address(request):
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('create')
    else:
        form = AddressForm()
    return render(request, 'create/create_address.html', {'form': form})


@login_required
def create_validator(request):
    if request.method == 'POST':
        form = ValidatorForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('create')
    else:
        form = ValidatorForm()
    return render(request, 'create/create_validator.html', {'form': form})


@login_required
def create_block(request):
    if request.method == 'POST':
        form = BlockForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('create')
    else:
        form = BlockForm()
    return render(request, 'create/create_block.html', {'form': form})


@login_required
def create_transaction(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('create')
    else:
        form = TransactionForm()
    return render(request, 'create/create_transaction.html', {'form': form})


@login_required
def create_transaction_data(request):
    if request.method == 'POST':
        form = TransactionDataForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('create')
    else:
        form = TransactionDataForm()
    return render(request, 'create/create_transaction_data.html', {'form': form})


@login_required
def create_contract(request):
    if request.method == 'POST':
        form = ContractForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('create')
    else:
        form = ContractForm()
    return render(request, 'create/create_contract.html', {'form': form})


@login_required
def create_contract_data(request):
    if request.method == 'POST':
        form = ContractDataForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('create')
    else:
        form = ContractDataForm()
    return render(request, 'create/create_contract_data.html', {'form': form})


@login_required
def create_token(request):
    if request.method == 'POST':
        form = TokenForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('create')
    else:
        form = TokenForm()
    return render(request, 'create/create_token.html', {'form': form})


@login_required
def create_mempool(request):
    if request.method == 'POST':
        form = MempoolForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('create')
    else:
        form = MempoolForm()
    return render(request, 'create/create_mempool.html', {'form': form})


def get_by_entity(request, template_name, repository):
    key = request.GET.get('key')
    if key:
        try:
            entity_instance = repository.get_by_id(key)
            if entity_instance:
                entity_dict = {field.name: getattr(entity_instance, field.name) for field in entity_instance._meta.fields}
                return render(request, template_name, {'entity': entity_dict})
            else:
                return render(request, template_name, {'error': 'Entity not found'})
        except Exception as e:
            return render(request, template_name, {'error': str(e)})
    return render(request, template_name)

def get_by_address(request):
    return get_by_entity(request, 'get_by/get_by_address.html', Repository.address())

def get_by_validator(request):
    return get_by_entity(request, 'get_by/get_by_validator.html', Repository.validator())

def get_by_block(request):
    return get_by_entity(request, 'get_by/get_by_block.html', Repository.block())

def get_by_transaction(request):
    return get_by_entity(request, 'get_by/get_by_transaction.html', Repository.transaction())

def get_by_transaction_data(request):
    return get_by_entity(request, 'get_by/get_by_transaction_data.html', Repository.transaction_data())

def get_by_contract(request):
    return get_by_entity(request, 'get_by/get_by_contract.html', Repository.contract())

def get_by_contract_data(request):
    return get_by_entity(request, 'get_by/get_by_contract_data.html', Repository.contract_data())

def get_by_token(request):
    return get_by_entity(request, 'get_by/get_by_token.html', Repository.token())

def get_by_mempool(request):
    return get_by_entity(request, 'get_by/get_by_mempool.html', Repository.mempool())

def get_all_address(request):
    addresses = Repository.address().get_all()
    return render(request, 'get_all/get_all_address.html', {'addresses': addresses})

def get_all_block(request):
    blocks = Repository.block().get_all()
    return render(request, 'get_all/get_all_block.html', {'blocks': blocks})

def get_all_validator(request):
    validators = Repository.validator().get_all()
    return render(request, 'get_all/get_all_validator.html', {'validators': validators})

def get_all_transaction(request):
    transactions = Repository.transaction().get_all()
    return render(request, 'get_all/get_all_transaction.html', {'transactions': transactions})

def get_all_transaction_data(request):
    transaction_data_list = Repository.transaction_data().get_all()
    status_choices = TransactionData.STATUS_CHOICES
    return render(request, 'get_all/get_all_transaction_data.html', {
        'transaction_data': transaction_data_list,
        'status_choices': status_choices
    })


def get_all_contract(request):
    contracts = Repository.contract().get_all()
    return render(request, 'get_all/get_all_contract.html', {'contracts': contracts})

def get_all_contract_data(request):
    contract_data_list = Repository.contract_data().get_all()
    return render(request, 'get_all/get_all_contract_data.html', {'contract_data_list': contract_data_list})

def get_all_token(request):
    tokens = Repository.token().get_all()
    return render(request, 'get_all/get_all_token.html', {'tokens': tokens})

def get_all_mempool(request):
    mempool_list = Repository.mempool().get_all()
    return render(request, 'get_all/get_all_mempool.html', {'mempool_list': mempool_list})

@login_required
def update_address(request, pk):
    instance = Repository.address().get_by_id(pk)
    if instance:
        eth_balance = request.GET.get('eth_balance', instance.eth_balance)

        instance.eth_balance = eth_balance
        Repository.address().update(pk, eth_balance=eth_balance)

        return redirect('get_all_address')
    return redirect('get_all_address')

@login_required
def delete_address(request, pk):
    Repository.address().delete(pk)
    return redirect('get_all_address')

@login_required
def update_validator(request, pk):
    instance = Repository.validator().get_by_id(pk)
    if instance:
        if request.method == 'POST':
            withdrawal_address_value = request.POST.get('withdrawal_address', instance.withdrawal_address.address)
            eth_staked = request.POST.get('eth_staked', instance.eth_staked)
            status = request.POST.get('status', instance.status)
            slashed = request.POST.get('slashed', 'off') == 'on'

            # Отримуємо об'єкт Address для withdrawal_address
            withdrawal_address_instance = Repository.address().get_by_id(withdrawal_address_value)
            if withdrawal_address_instance:
                instance.withdrawal_address = withdrawal_address_instance

            # Оновлюємо інші поля
            instance.eth_staked = eth_staked
            instance.status = status
            instance.slashed = slashed

            # Зберігаємо зміни
            instance.save()
            return redirect('get_all_validator')
    return redirect('get_all_validator')



@login_required
def delete_validator(request, pk):
    Repository.validator().delete(pk)
    return redirect('get_all_validator')

@login_required
def update_block(request, pk):
    instance = Repository.block().get_by_id(pk)
    if instance:
        if request.method == 'POST':
            status = request.POST.get('status', instance.status)
            epoch = request.POST.get('epoch', instance.epoch)
            slot = request.POST.get('slot', instance.slot)
            reward = request.POST.get('reward', instance.reward)
            difficulty = request.POST.get('difficulty', instance.difficulty)
            height = request.POST.get('height', instance.height)
            nonce = request.POST.get('nonce', instance.nonce)

            # Оновлюємо поля інстансу
            instance.status = status
            instance.epoch = epoch
            instance.slot = slot
            instance.reward = reward
            instance.difficulty = difficulty
            instance.height = height
            instance.nonce = nonce

            # Зберігаємо зміни
            instance.save()
            return redirect('get_all_block')
    return redirect('get_all_block')

@login_required
def delete_block(request, pk):
    Repository.block().delete(pk)
    return redirect('get_all_block')

@login_required
def update_transaction(request, pk):
    instance = Repository.transaction().get_by_id(pk)
    if instance:
        block = request.GET.get('block', instance.block)

        Repository.transaction().update(pk, block=block)
        return redirect('get_all_transaction')
    return redirect('get_all_transaction')

@login_required
def delete_transaction(request, pk):
    transaction = Repository.transaction().get_by_id(pk)
    if transaction:
        try:
            transaction_data = transaction.transactiondata
            transaction_data.delete()
        except TransactionData.DoesNotExist:
            pass
        transaction.delete()
    return redirect('get_all_transaction')

@login_required
def update_transaction_data(request, pk):
    instance = Repository.transaction_data().get_by_id(pk)
    if instance:
        status = request.GET.get('status', instance.status)
        value = request.GET.get('value', instance.value)
        eth_price = request.GET.get('eth_price', instance.eth_price)

        Repository.transaction_data().update(pk, status=status, value=value, eth_price=eth_price)
        return redirect('get_all_transaction_data')
    return redirect('get_all_transaction_data')

@login_required
def delete_transaction_data(request, pk):
    transaction_data = Repository.transaction_data().get_by_id(pk)
    if transaction_data:
        transaction = transaction_data.transaction
        # Видаляємо TransactionData
        transaction_data.delete()
        # Пробуємо видалити пов'язану транзакцію
        try:
            transaction.delete()
        except RestrictedError:
            # Якщо транзакцію не можна видалити, продовжуємо без помилок
            pass
    return redirect('get_all_transaction_data')

@login_required
def update_contract(request, pk):
    instance = Repository.contract().get_by_id(pk)
    if instance:
        creator_address = request.GET.get('creator_address', instance.creator_address)

        Repository.contract().update(pk, creator_address=creator_address)
        return redirect('get_all_contract')
    return redirect('get_all_contract')

@login_required
def delete_contract(request, pk):
    Repository.contract().delete(pk)
    return redirect('get_all_contract')

@login_required
def update_contract_data(request, pk):
    instance = Repository.contract_data().get_by_id(pk)
    if instance:
        if request.method == 'POST':
            source_code = request.POST.get('source_code', instance.source_code)
            bytecode = request.POST.get('bytecode', instance.bytecode)
            name = request.POST.get('name', instance.name)
            version = request.POST.get('version', instance.version)

            # Оновлюємо поля
            instance.source_code = source_code
            instance.bytecode = bytecode
            instance.name = name
            instance.version = version

            # Зберігаємо зміни
            instance.save()
            return redirect('get_all_contract_data')
    return redirect('get_all_contract_data')

@login_required
def delete_contract_data(request, pk):
    Repository.contract_data().delete(pk)
    return redirect('get_all_contract_data')

@login_required
def update_token(request, pk):
    instance = Repository.token().get_by_id(pk)
    if instance:
        if request.method == 'POST':
            symbol = request.POST.get('symbol', instance.symbol)
            supply = request.POST.get('supply', instance.supply)
            decimals = request.POST.get('decimals', instance.decimals)
            type_value = request.POST.get('type', instance.type)

            # Оновлюємо поля
            instance.symbol = symbol
            instance.supply = supply
            instance.decimals = decimals
            instance.type = type_value

            # Зберігаємо зміни
            instance.save()
            return redirect('get_all_token')
    return redirect('get_all_token')

@login_required
def delete_token(request, pk):
    Repository.token().delete(pk)
    return redirect('get_all_token')

@login_required
def update_mempool(request, pk):
    instance = Repository.mempool().get_by_id(pk)
    return redirect('get_all_mempool')

@login_required
def delete_mempool(request, pk):
    Repository.mempool().delete(pk)
    return redirect('get_all_mempool')


class AddressDetail(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self,request, pk):
        address = Repository.address().get_by_id(pk)
        if address:
            return Response(
                {"address": address.address, "eth_balance": str(address.eth_balance)},
                status=status.HTTP_200_OK,
            )
        return Response({"error": "Address not found"}, status=status.HTTP_404_NOT_FOUND)

    def post(self,request):
        address = request.data.get("address")
        eth_balance = request.data.get("eth_balance", 0)

        if not address:
            return Response({"error": "Address is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            new_address = Repository.address().create(address, eth_balance)
            return Response(
                {"address": new_address.address, "eth_balance": str(new_address.eth_balance)},
                status=status.HTTP_201_CREATED,
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def put(self,request, pk):
        eth_balance = request.data.get("eth_balance")
        if eth_balance is None:
            return Response({"error": "eth_balance is required"}, status=status.HTTP_400_BAD_REQUEST)

        updated_address = Repository.address().update(pk, eth_balance=eth_balance)
        if updated_address:
            return Response(
                {"address": updated_address.address, "eth_balance": str(updated_address.eth_balance)},
                status=status.HTTP_200_OK,
            )
        return Response({"error": "Address not found"}, status=status.HTTP_404_NOT_FOUND)


    def delete(self,request, pk):
        if Repository.address().delete(pk):
            return Response({"message": "Address deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        return Response({"error": "Address not found"}, status=status.HTTP_404_NOT_FOUND)


class ValidatorDetail(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        validator = Repository.validator().get_by_id(pk)
        if validator:
            return Response({
                "validator_id": validator.validator_id,
                "address": validator.address.address,
                "withdrawal_address": validator.withdrawal_address.address,
                "eth_staked": str(validator.eth_staked),
                "status": validator.status,
                "slashed": validator.slashed
            }, status=status.HTTP_200_OK)
        return Response({"error": "Validator not found"}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        address = request.data.get("address")
        withdrawal_address = request.data.get("withdrawal_address")
        eth_staked = request.data.get("eth_staked")
        status_value = request.data.get("status")
        slashed = request.data.get("slashed", False)

        if not all([address, withdrawal_address, eth_staked, status_value]):
            return Response({"error": "All fields are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            new_validator = Repository.validator().create(
                address=address,
                withdrawal_address=withdrawal_address,
                eth_staked=eth_staked,
                status=status_value,
                slashed=slashed
            )
            return Response({
                "validator_id": new_validator.validator_id,
                "address": new_validator.address.address,
                "withdrawal_address": new_validator.withdrawal_address.address,
                "eth_staked": str(new_validator.eth_staked),
                "status": new_validator.status,
                "slashed": new_validator.slashed
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):

        validator = Repository.validator().get_by_id(pk)
        if not validator:
            return Response({"error": "Validator not found"}, status=status.HTTP_404_NOT_FOUND)

        address_value = request.data.get("address", validator.address.address)
        withdrawal_address_value = request.data.get("withdrawal_address", validator.withdrawal_address.address)
        eth_staked = request.data.get("eth_staked", validator.eth_staked)
        status_value = request.data.get("status", validator.status)
        slashed = request.data.get("slashed", validator.slashed)

        try:
            address_instance = Repository.address().get_by_id(address_value)
            withdrawal_address_instance = Repository.address().get_by_id(withdrawal_address_value)

            if not address_instance or not withdrawal_address_instance:
                return Response({"error": "Address or withdrawal address not found"},
                                status=status.HTTP_400_BAD_REQUEST)

            updated_validator = Repository.validator().update(
                pk,
                address=address_instance,
                withdrawal_address=withdrawal_address_instance,
                eth_staked=eth_staked,
                status=status_value,
                slashed=slashed
            )

            return Response({
                "validator_id": updated_validator.validator_id,
                "address": updated_validator.address.address,
                "withdrawal_address": updated_validator.withdrawal_address.address,
                "eth_staked": str(updated_validator.eth_staked),
                "status": updated_validator.status,
                "slashed": updated_validator.slashed
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        if Repository.validator().delete(pk):
            return Response({"message": "Validator deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        return Response({"error": "Validator not found"}, status=status.HTTP_404_NOT_FOUND)

class MempoolDetail(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        mempool = Repository.mempool().get_by_id(pk)
        if mempool:
            return Response(
                {
                    "transaction_hash": mempool.transaction.transaction_hash,
                },
                status=status.HTTP_200_OK,
            )
        return Response({"error": "Mempool transaction not found"}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        transaction_hash = request.data.get("transaction_hash")

        if not transaction_hash:
            return Response({"error": "Transaction hash is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            transaction_instance = Repository.transaction().get_by_id(transaction_hash)

            if not transaction_instance:
                return Response({"error": "Transaction not found"}, status=status.HTTP_400_BAD_REQUEST)

            new_mempool = Repository.mempool().create(transaction=transaction_instance)

            return Response(
                {
                    "transaction_hash": new_mempool.transaction.transaction_hash,
                },
                status=status.HTTP_201_CREATED,
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        mempool = Repository.mempool().get_by_id(pk)
        if not mempool:
            return Response({"error": "Mempool transaction not found"}, status=status.HTTP_404_NOT_FOUND)

        transaction_hash = request.data.get("transaction_hash", mempool.transaction.transaction_hash)

        try:
            transaction_instance = Repository.transaction().get_by_id(transaction_hash)

            if not transaction_instance:
                return Response({"error": "Transaction not found"}, status=status.HTTP_400_BAD_REQUEST)

            updated_mempool = Repository.mempool().update(
                pk, transaction=transaction_instance
            )

            return Response(
                {
                    "transaction_hash": updated_mempool.transaction.transaction_hash,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        if Repository.mempool().delete(pk):
            return Response({"message": "Mempool transaction deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        return Response({"error": "Mempool transaction not found"}, status=status.HTTP_404_NOT_FOUND)



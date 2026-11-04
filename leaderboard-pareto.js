/* The chart uses the same selected trials and unrounded costs as the table. */
(() => {
  'use strict';
  const colors = ['#16847c', '#bd7b27', '#3976c6', '#9562bb', '#bd5b76'];
  const money = value => value.toLocaleString('en-US', {style: 'currency', currency: 'USD'});
  const frontier = entries => entries.filter(entry => !entries.some(other =>
    other.cost <= entry.cost && other.score >= entry.score &&
    (other.cost < entry.cost || other.score > entry.score)
  )).sort((a, b) => a.cost - b.cost || b.score - a.score);

  function svgNode(tag, attributes = {}, text) {
    const node = document.createElementNS('http://www.w3.org/2000/svg', tag);
    Object.entries(attributes).forEach(([key, value]) => node.setAttribute(key, value));
    if (text != null) node.textContent = text;
    return node;
  }

  function render(entries, taskCount) {
    const chart = document.getElementById('pareto-chart');
    const legend = document.getElementById('pareto-legend');
    const eligible = entries.filter(e => e.trials.length === taskCount && taskCount > 0 &&
      Number.isFinite(e.cost) && e.cost >= 0 && Number.isFinite(e.score));
    const visible = eligible.filter(e => e.visible);
    chart.replaceChildren();
    legend.replaceChildren();
    document.getElementById('pareto-empty').hidden = visible.length > 0;
    chart.hidden = visible.length === 0;
    if (!visible.length) return;
    legend.style.setProperty('--pareto-columns', Math.min(4, visible.length));

    // Search hides models, but does not turn a dominated model into a frontier point.
    const frontierIds = new Set(frontier(eligible).map(e => e.id));
    const width = Math.max(300, chart.clientWidth), height = width < 600 ? 330 : 420;
    const left = 58, right = width - 32, top = 42, bottom = height - 54;
    const minCost = Math.min(...eligible.map(e => e.cost));
    const maxCost = Math.max(...eligible.map(e => e.cost));
    const logarithmic = minCost > 0;
    const xMin = logarithmic ? minCost / 1.25 : 0;
    const xMax = Math.max(logarithmic ? maxCost * 1.25 : maxCost * 1.1, 0.01);
    const transform = value => logarithmic ? Math.log10(value) : value;
    const x = value => left + (transform(value) - transform(xMin)) /
      (transform(xMax) - transform(xMin)) * (right - left);
    const yMax = Math.min(100, Math.max(5, Math.ceil(Math.max(...eligible.map(e => e.score)) * 1.15 / 5) * 5));
    const y = value => bottom - value / yMax * (bottom - top);
    const svg = svgNode('svg', {viewBox: `0 0 ${width} ${height}`, 'aria-labelledby': 'pareto-title pareto-description'});
    svg.append(svgNode('title', {id: 'pareto-title'}, 'Mean task score versus total agent cost'));
    svg.append(svgNode('desc', {id: 'pareto-description'},
      `Costs cover the same ${taskCount} selected tasks as the table. Higher scores and lower costs are better. ` +
      'The frontier connects models for which no model has both an equal or higher score and an equal or lower cost, with at least one strict improvement. Select a model to open its results.'));
    svg.append(svgNode('text', {x: left, y: 18, class: 'pareto-axis-label'}, 'Mean task score (0–100)'));
    const yStep = yMax <= 25 ? 5 : yMax <= 50 ? 10 : 20;
    for (let tick = 0; tick <= yMax; tick += yStep) {
      svg.append(svgNode('line', {x1: left, x2: right, y1: y(tick), y2: y(tick), class: 'pareto-grid'}));
      svg.append(svgNode('text', {x: left - 12, y: y(tick) + 4, 'text-anchor': 'end', class: 'pareto-tick'}, String(tick)));
    }
    let ticks = [];
    if (logarithmic) {
      for (let power = Math.floor(Math.log10(xMin)); power <= Math.ceil(Math.log10(xMax)); power++) {
        for (const multiple of [1, 2, 5]) {
          const value = multiple * 10 ** power;
          if (value >= xMin && value <= xMax) ticks.push(value);
        }
      }
    } else {
      ticks = Array.from({length: 5}, (_, i) => xMax * i / 4);
    }
    // Keep tick labels readable on small screens.
    if (width < 600 && ticks.length > 4) ticks = ticks.filter((_, i) => i % 2 === 0);
    ticks.forEach(tick => {
      svg.append(svgNode('line', {x1: x(tick), x2: x(tick), y1: top, y2: bottom, class: 'pareto-grid pareto-grid-vertical'}));
      const label = '$' + tick.toLocaleString('en-US', {maximumFractionDigits: tick < 1 ? 3 : tick < 10 ? 2 : 0});
      svg.append(svgNode('text', {x: x(tick), y: bottom + 23, 'text-anchor': 'middle', class: 'pareto-tick'}, label));
    });
    svg.append(svgNode('text', {x: (left + right) / 2, y: height - 6, 'text-anchor': 'middle', class: 'pareto-axis-label'},
      `Cost (USD${logarithmic ? ', log scale' : ''})`));
    const line = frontier(eligible).filter(e => e.visible);
    if (line.length > 1) {
      svg.append(svgNode('path', {class: 'pareto-frontier', d: line.map((e, i) => `${i ? 'L' : 'M'}${x(e.cost)},${y(e.score)}`).join(' ')}));
    }
    const tooltip = document.createElement('div');
    tooltip.className = 'pareto-tooltip';
    tooltip.hidden = true;
    tooltip.setAttribute('aria-hidden', 'true');

    visible.forEach(entry => {
      const color = colors[entry.colorIndex % colors.length];
      const onFrontier = frontierIds.has(entry.id);
      const label = `${entry.name} (${entry.effort})`;
      const summary = `${entry.score.toFixed(1)} · ${money(entry.cost)}`;
      const link = svgNode('a', {href: entry.url, tabindex: 0, class: 'pareto-point',
        'data-entry': entry.id, 'data-cost': entry.cost, 'data-score': entry.score,
        'data-frontier': onFrontier, 'aria-label': `${label}: ${summary}${onFrontier ? ', Pareto frontier' : ''}. View results.`});
      if (onFrontier) link.append(svgNode('circle', {cx: x(entry.cost), cy: y(entry.score), r: 11, fill: color, opacity: '.13'}));
      link.append(svgNode('circle', {cx: x(entry.cost), cy: y(entry.score), r: 6, fill: color, class: 'pareto-dot'}));
      const end = x(entry.cost) > width * .6;
      link.append(svgNode('text', {x: x(entry.cost) + (end ? -14 : 14), y: y(entry.score) - 12,
        'text-anchor': end ? 'end' : 'start', class: 'pareto-point-label'}, entry.name));
      const showTooltip = () => {
        const name = document.createElement('strong');
        name.textContent = label;
        const details = document.createElement('span');
        details.textContent = `${summary} · ${taskCount} tasks`;
        tooltip.replaceChildren(name, details);
        tooltip.hidden = false;
        tooltip.style.left = `${Math.max(8, Math.min(x(entry.cost) + 14, width - tooltip.offsetWidth - 8))}px`;
        tooltip.style.top = `${Math.max(0, y(entry.score) - tooltip.offsetHeight - 18)}px`;
      };
      link.addEventListener('mouseenter', showTooltip);
      link.addEventListener('focus', showTooltip);
      link.addEventListener('mouseleave', () => { tooltip.hidden = true; });
      link.addEventListener('blur', () => { tooltip.hidden = true; });
      svg.append(link);

      const item = document.createElement('a');
      item.href = entry.url;
      item.className = 'pareto-legend-item';
      const dot = document.createElement('span');
      dot.className = 'pareto-legend-dot';
      dot.style.backgroundColor = color;
      const name = document.createElement('span');
      name.textContent = label;
      const details = document.createElement('span');
      details.className = 'pareto-legend-summary';
      details.textContent = summary;
      item.append(dot, name, details);
      legend.append(item);
    });
    chart.append(svg, tooltip);
    // Keep nearby model labels apart; the legend retains every model on crowded charts.
    const occupied = visible.map(e => ({x: x(e.cost) - 9, y: y(e.score) - 9, width: 18, height: 18}));
    const overlaps = (a, b) => a.x < b.x + b.width + 4 && a.x + a.width + 4 > b.x &&
      a.y < b.y + b.height + 4 && a.y + a.height + 4 > b.y;
    const labels = [...svg.querySelectorAll('.pareto-point-label')]
      .sort((a, b) => Number(a.getAttribute('y')) - Number(b.getAttribute('y')) || a.textContent.localeCompare(b.textContent));
    labels.forEach(label => {
      if (!label.getBBox().width) return; // Point labels are hidden on mobile.
      const originalY = Number(label.getAttribute('y'));
      for (const offset of [0, 36, -22, 58]) {
        label.setAttribute('y', originalY + offset);
        const box = label.getBBox();
        if (box.x >= 0 && box.x + box.width <= width && box.y >= top && box.y + box.height <= bottom &&
            !occupied.some(other => overlaps(box, other))) {
          occupied.push(box);
          return;
        }
      }
      label.style.display = 'none';
    });
  }
  window.SearchSwePareto = {render, frontier};
})();

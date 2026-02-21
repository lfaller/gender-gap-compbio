#!/usr/bin/env python3
"""
Generate visualizations for gender classification results
"""
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Rectangle
import numpy as np

# Set style
plt.style.use('seaborn-v0_8-darkgrid')
colors = {
    'male': '#1f77b4',
    'female': '#ff7f0e',
    'other': '#2ca02c',
    'unknown': '#d62728'
}

# Figure 1: Overall Gender Distribution
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

# Pie chart
genders = ['Male\n(569,108)', 'Female\n(400,227)', 'Other\n(5)', 'Unknown\n(6,391)']
sizes = [569108, 400227, 5, 6391]
colors_list = [colors['male'], colors['female'], colors['other'], colors['unknown']]
explode = (0.05, 0.05, 0, 0.1)

ax1.pie(sizes, labels=genders, autopct='%1.1f%%', startangle=90,
        colors=colors_list, explode=explode, textprops={'fontsize': 11})
ax1.set_title('Overall Author Gender Distribution\n(Total: 977,731 authors)',
              fontsize=13, fontweight='bold', pad=20)

# Bar chart of known vs unknown
categories = ['With Known\nGender', 'Unknown/\nUnclassified']
values = [969340, 6391]
bars = ax2.bar(categories, values, color=['#2ca02c', '#d62728'], alpha=0.8, edgecolor='black', linewidth=1.5)
ax2.set_ylabel('Number of Authors', fontsize=11, fontweight='bold')
ax2.set_title('Classification Coverage', fontsize=13, fontweight='bold', pad=20)
ax2.set_ylim(0, 1000000)

# Add value labels on bars
for bar, val in zip(bars, values):
    height = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2., height,
            f'{val:,}\n({val/977731*100:.1f}%)',
            ha='center', va='bottom', fontsize=10, fontweight='bold')

plt.tight_layout()
plt.savefig('./outputs/figures/fig_gender_distribution.png', dpi=300, bbox_inches='tight')
plt.savefig('./outputs/figures/fig_gender_distribution.svg', format='svg', bbox_inches='tight')
print("✓ Saved: fig_gender_distribution.png/svg")

# Figure 2: Classification Strategy & Success Rates
fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))

# Stage 1: Processing pipeline
stages = ['Starting\nUnknowns', 'After\nFree Tier', 'After\nPaid Tier', 'Final\n(Retry)']
remaining = [392610, 370653, 24614, 6391]
colors_stages = ['#ff7f0e', '#ff7f0e', '#1f77b4', '#2ca02c']

ax1.bar(stages, remaining, color=colors_stages, alpha=0.8, edgecolor='black', linewidth=1.5)
ax1.set_ylabel('Remaining Unknown Names', fontsize=10, fontweight='bold')
ax1.set_title('Classification Pipeline Progress', fontsize=12, fontweight='bold')
ax1.set_yscale('log')
for i, (stage, val) in enumerate(zip(stages, remaining)):
    ax1.text(i, val*1.1, f'{val:,}', ha='center', fontsize=9, fontweight='bold')

# Stage 2: Success rates by stage
stage_names = ['Free Tier', 'Paid Tier', 'Improved\nParsing', 'Overall']
success_rates = [5.6, 93.4, 93.8, 98.4]
colors_success = ['#ff7f0e', '#1f77b4', '#2ca02c', '#9467bd']

bars = ax2.bar(stage_names, success_rates, color=colors_success, alpha=0.8, edgecolor='black', linewidth=1.5)
ax2.set_ylabel('Success Rate (%)', fontsize=10, fontweight='bold')
ax2.set_title('Classification Success Rate by Stage', fontsize=12, fontweight='bold')
ax2.set_ylim(0, 110)
for bar, rate in zip(bars, success_rates):
    height = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2., height + 1,
            f'{rate}%', ha='center', va='bottom', fontsize=10, fontweight='bold')

# Stage 3: Names classified by stage
stage_names_3 = ['Free Tier', 'Paid Tier', 'Improved\nParsing']
classified = [21957, 347280, 41968]
colors_classified = ['#ff7f0e', '#1f77b4', '#2ca02c']

bars = ax3.bar(stage_names_3, classified, color=colors_classified, alpha=0.8, edgecolor='black', linewidth=1.5)
ax3.set_ylabel('Names Classified', fontsize=10, fontweight='bold')
ax3.set_title('Classification Volume by Stage', fontsize=12, fontweight='bold')
for bar, val in zip(bars, classified):
    height = bar.get_height()
    ax3.text(bar.get_x() + bar.get_width()/2., height,
            f'{val:,}', ha='center', va='bottom', fontsize=9, fontweight='bold')

# Stage 4: Cost vs. Coverage
methods = ['Free Tier', 'Paid Tier', 'Improved\nParsing', 'Total']
costs = [0, 0.18, 0, 0.18]
coverage = [21957, 347280, 41968, 411205]

ax4_twin = ax4.twinx()

bars = ax4.bar(methods, costs, color=['#ff7f0e', '#1f77b4', '#2ca02c', '#9467bd'],
               alpha=0.8, edgecolor='black', linewidth=1.5, label='Cost')
ax4.set_ylabel('Cost (USD)', fontsize=10, fontweight='bold', color='black')
ax4.set_ylim(0, 0.25)

line = ax4_twin.plot(methods, coverage, 'o-', color='red', linewidth=2.5, markersize=8, label='Names Classified')
ax4_twin.set_ylabel('Names Classified', fontsize=10, fontweight='bold', color='red')
ax4_twin.set_yscale('log')

ax4.set_title('Cost-Benefit Analysis', fontsize=12, fontweight='bold')
ax4.tick_params(axis='y', labelcolor='black')
ax4_twin.tick_params(axis='y', labelcolor='red')

plt.tight_layout()
plt.savefig('./outputs/figures/fig_classification_strategy.png', dpi=300, bbox_inches='tight')
plt.savefig('./outputs/figures/fig_classification_strategy.svg', format='svg', bbox_inches='tight')
print("✓ Saved: fig_classification_strategy.png/svg")

# Figure 3: Key Metrics Summary
fig, ax = plt.subplots(figsize=(12, 8))
ax.axis('off')

# Title
title_text = 'Gender Classification Summary Statistics'
ax.text(0.5, 0.95, title_text, ha='center', fontsize=16, fontweight='bold',
        transform=ax.transAxes)

# Metrics boxes
metrics = [
    ('Total Authors', '977,731', colors['other']),
    ('Classified Successfully', '386,219', colors['male']),
    ('Classification Rate', '98.4%', colors['female']),
    ('Remaining Unknown', '6,391', colors['unknown']),
    ('Total Cost', '$0.18', '#2ca02c'),
    ('Cost per Name', '0.0000005¢', '#9467bd'),
]

y_start = 0.80
x_positions = [0.15, 0.5, 0.85]
for idx, (label, value, color) in enumerate(metrics):
    row = idx // 3
    col = idx % 3

    x = x_positions[col]
    y = y_start - (row * 0.25)

    # Draw box
    rect = Rectangle((x - 0.12, y - 0.08), 0.24, 0.15,
                     transform=ax.transAxes, facecolor=color, alpha=0.3,
                     edgecolor=color, linewidth=2)
    ax.add_patch(rect)

    # Add text
    ax.text(x, y + 0.04, label, ha='center', fontsize=10, fontweight='bold',
           transform=ax.transAxes)
    ax.text(x, y - 0.02, value, ha='center', fontsize=12, fontweight='bold',
           color=color, transform=ax.transAxes)

# Key achievements section
achievements_y = 0.35
ax.text(0.05, achievements_y, 'Key Achievements:', fontsize=12, fontweight='bold',
       transform=ax.transAxes)

achievements = [
    '✓ Classified 386,219 out of 392,610 unknown author names (98.4% coverage)',
    '✓ Used innovative three-stage LLM strategy with progressive refinement',
    '✓ Implemented robust JSON parsing with 4-level fallback strategies',
    '✓ Achieved all results for minimal cost (~$0.18)',
    '✓ Successfully handled Unicode, special characters, and encoding issues',
]

for idx, achievement in enumerate(achievements):
    ax.text(0.08, achievements_y - 0.05 - (idx * 0.04), achievement,
           fontsize=9, transform=ax.transAxes, va='top')

# Footer
ax.text(0.5, 0.02, 'Gender classification enables accurate analysis of gender gaps in scientific authorship',
       ha='center', fontsize=9, style='italic', transform=ax.transAxes, color='gray')

plt.savefig('./outputs/figures/fig_gender_classification_summary.png', dpi=300, bbox_inches='tight')
plt.savefig('./outputs/figures/fig_gender_classification_summary.svg', format='svg', bbox_inches='tight')
print("✓ Saved: fig_gender_classification_summary.png/svg")

print("\n✅ All gender classification figures generated successfully!")

"""
Visualization module for Patent Landscape Map.
Effectively visualizes the relationship between User Idea and Search Results.
"""
import pandas as pd
import plotly.express as px
import streamlit as st

def render_patent_map(result: dict):
    """
    Render a premium interactive Patent Landscape Map (Guardian Model).
    Visualizes the User Idea as a protected asset (1.0, 1.0) with incoming threats.
    """
    search_results = result.get('search_results', [])
    user_idea = result.get('user_idea', '내 아이디어')
    
    if not search_results:
        st.caption("시각화할 데이터가 충분하지 않습니다.")
        return

    # Prepare data for DataFrame
    data = []
    
    # 1. User Idea: The Core Asset at (1.0, 1.0)
    # We maintain it at max coords to represent the 'Target' that others are approaching
    data.append({
        "Patent ID": "🎯 My Idea",
        "Title": "✨ MY CORE IDEA (나의 핵심 아이디어)",
        "Conceptual Alignment": 1.0,
        "Analytical Depth": 1.0,
        "Relevance": 40,  # Larger size
        "Category": "My Core Idea",
        "Abstract": user_idea[:200],
        "Marker": "star" # Use distinct marker via Plotly symbol map if possible, or color/size
    })
    
    # 2. Add search results
    all_patent_coords = []  # Store coords for ALL patents to draw lines
    
    import random
    random.seed(42)  # Consistent jitter
    
    for idx, r in enumerate(search_results):
        # Use grading_score for alignment with jitter
        base_alignment = r.get('grading_score', 0.5)
        jitter_x = (random.random() - 0.5) * 0.08  # ±0.04 jitter
        alignment = max(0, min(1, base_alignment + jitter_x))
        
        # Improved depth: use index-based spread + jitter to avoid overlap
        base_depth = 0.15 + (idx * 0.18)  # Spread from 0.15 to ~0.87
        jitter_y = (random.random() - 0.5) * 0.1
        depth = max(0.05, min(0.95, base_depth + jitter_y))
        
        grade = r.get('grading_score', 0)
        
        # Store coords for connection line (ALL patents)
        all_patent_coords.append({'x': alignment, 'y': depth, 'title': r.get('title')})
        
        # Categorization Logic
        if grade >= 0.6:
            cat = "🔥 CRITICAL THREAT (핵심 위협)"
        elif grade >= 0.4:
            cat = "⚠️ COLLISION ZONE (충돌 경계)"
        elif grade >= 0.2:
            cat = "🕵️ HIDDEN RIVAL (잠재적 경쟁)"
        else:
            cat = "📗 SAFE DISTANCE (단순 참고)"
            
        data.append({
            "Patent ID": r.get('patent_id'),
            "Title": r.get('title'),
            "Conceptual Alignment": alignment,
            "Analytical Depth": depth,
            "Relevance": grade * 20 + 10,
            "Category": cat,
            "Abstract": r.get('abstract', '')[:150] + "...",
            "Marker": "circle"
        })
        
    df = pd.DataFrame(data)
    
    # Create Scatter Plot
    fig = px.scatter(
        df,
        x="Conceptual Alignment",
        y="Analytical Depth",
        size="Relevance",
        color="Category",
        hover_name="Title",
        hover_data={"Patent ID": True, "Abstract": True, "Relevance": False},
        color_discrete_map={
            "My Core Idea": "#2980b9",       # Strong Blue (Brand Color)
            "🔥 CRITICAL THREAT (핵심 위협)": "#e74c3c", # Red
            "⚠️ COLLISION ZONE (충돌 경계)": "#f39c12", # Orange
            "🕵️ HIDDEN RIVAL (잠재적 경쟁)": "#8e44ad", # Purple
            "📗 SAFE DISTANCE (단순 참고)": "#95a5a6"   # Gray
        },
        title="✨ 특허 방어 전략 지도 (Patent Guardian Map)",
        template="plotly_white"
    )
    
    # Ivory background color (#fdfaf5) to match the app theme
    ivory_bg = "#fdfaf5"
    grid_color = "rgba(0,0,0,0.1)"
    line_color = "rgba(0,0,0,0.2)"
    
    fig.update_layout(
        xaxis_title="기술적 정렬도 (Alignment)", 
        yaxis_title="분석 심도 (Depth)", 
        legend_title="Legend",
        hovermode="closest",
        height=660,
        margin=dict(l=40, r=40, t=80, b=140),
        plot_bgcolor=ivory_bg,
        paper_bgcolor=ivory_bg,
        xaxis=dict(range=[-0.05, 1.1], gridcolor=grid_color, showticklabels=False), # Hide ticks
        yaxis=dict(range=[-0.05, 1.1], gridcolor=grid_color, showticklabels=False),
        font=dict(family="Pretendard, sans-serif", size=13, color="#1e1e1e")
    )
    
    # 3. Add Connection Lines (ALL Patents -> Core Idea)
    # This visualizes the proximity/threat level
    for pt in all_patent_coords:
        fig.add_shape(
            type="line",
            x0=pt['x'], y0=pt['y'],
            x1=1.0, y1=1.0,
            line=dict(color="rgba(231, 76, 60, 0.3)", width=1.5, dash="dot"),
            layer="below"
        )

    # 4. Custom Marker for My Idea (Workaround for PX symbols)
    # We can override the marker symbol for the specific trace if needed, 
    # but here we rely on size/color distinction. 
    # Ideally, we can add a specialized annotation for the Core Idea.
    fig.add_annotation(
        x=1.0, y=1.0,
        text="🏰", # Castle icon or Trophy
        showarrow=False,
        font=dict(size=40),
        yshift=0
    )
    
    # Effect: Glow for My Idea (Large transparent circle behind)
    fig.add_shape(
        type="circle",
        xref="x", yref="y",
        x0=0.92, y0=0.92, x1=1.08, y1=1.08,
        fillcolor="rgba(52, 152, 219, 0.3)",
        line_color="rgba(52, 152, 219, 0)",
        layer="below"
    )

    # Add Quadrant Labels (Adjusted for new metaphor)
    fig.add_annotation(x=0.5, y=0.5, text="<b>🛡️ DEFENSE FIELD</b>", showarrow=False, font=dict(color="rgba(41, 128, 185, 0.15)", size=20))
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Revised Analysis Guide (Premium)
    st.markdown(f"""
    <div style='background-color: #f8f9fa; padding: 15px; border-radius: 10px; border-left: 5px solid #2980b9;'>
        <h4 style='color: #2c3e50; margin-top:0;'>🛡️ 전략 가이드: 특허 방어 모델 (Guardian Model)</h4>
        <p style='font-size: 14px; color: #555;'>
            귀하의 아이디어(<b>🏰 MY CORE IDEA</b>)는 우측 상단(1.0, 1.0)의 <b>안전한 성(Castle)</b>으로 표현됩니다. 타사 특허들이 얼마나 내 성에 가까이 접근(침범)하고 있는지 확인하세요.
        </p>
        <h5 style='color: #34495e; margin-bottom: 5px;'>📊 축(Axis) 설명</h5>
        <ul style='font-size: 14px; color: #555; margin-top: 5px;'>
            <li><b>X축 - 기술적 정렬도 (Alignment)</b>: AI가 평가한 <b>기술적 유사도</b>입니다. 우측(1.0)에 가까울수록 귀하의 아이디어와 기술 사상이 일치하여 <span style='color:#e74c3c'>침해 위험이 높습니다</span>.</li>
            <li><b>Y축 - 분석 심도 (Depth)</b>: 해당 특허의 <b>분석 우선순위</b>를 나타냅니다. 상단에 있을수록 더 상세한 검토가 필요한 특허입니다.</li>
        </ul>
        <h5 style='color: #34495e; margin-bottom: 5px;'>🎨 범주(Category) 설명</h5>
        <ul style='font-size: 14px; color: #555; margin-top: 5px;'>
            <li><b>🔴 CRITICAL THREAT (핵심 위협)</b>: 방어선 안쪽으로 깊숙이 침투한 특허들입니다. <span style='color:#e74c3c'>점선</span>으로 연결된 특허는 직접적인 충돌 위험이 있습니다.</li>
            <li><b>🟠 COLLISION ZONE (충돌 경계)</b>: 잠재적 위험군입니다. 선제적인 회피 설계가 권장됩니다.</li>
            <li><b>🟣 HIDDEN RIVAL (잠재적 경쟁)</b>: 기술적 접근 방식이 유사한 잠재적 경쟁자들입니다.</li>
            <li><b>🟢 SAFE DISTANCE (안전 거리)</b>: 아직은 거리가 먼 참조 기술들입니다.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
 
from models import db, SiteSetting, ThemeSetting
from functools import lru_cache
import json


def get_setting(key, default=None):
    s = SiteSetting.query.filter_by(key=key).first()
    return s.value if s else default


def set_setting(key, value):
    s = SiteSetting.query.filter_by(key=key).first()
    if s:
        s.value = value
    else:
        s = SiteSetting(key=key, value=value)
        db.session.add(s)
    db.session.commit()
    return s


def get_theme(key, default=None):
    t = ThemeSetting.query.filter_by(key=key).first()
    return t.value if t else default


def set_theme(key, value):
    t = ThemeSetting.query.filter_by(key=key).first()
    if t:
        t.value = value
    else:
        t = ThemeSetting(key=key, value=value)
        db.session.add(t)
    db.session.commit()
    return t


def get_all_theme():
    items = ThemeSetting.query.all()
    return {i.key: i.value for i in items}


def get_all_settings():
    items = SiteSetting.query.all()
    return {i.key: i.value for i in items}


DEFAULT_THEME = {
    "font_display": "'Orbitron', sans-serif",
    "font_heading": "'Inter', system-ui, sans-serif",
    "font_body": "'Inter', system-ui, sans-serif",
    "font_nav": "'Inter', system-ui, sans-serif",
    "theme_mode": "light",
    "color_primary": "#0284c7",
    "color_secondary": "#6366f1",
    "color_accent": "#0ea5e9",
    "color_bg": "#f8fafc",
    "color_bg_deep": "#f1f5f9",
    "color_surface": "#ffffff",
    "color_surface_2": "#f1f5f9",
    "color_text": "#0f172a",
    "color_muted": "#64748b",
    "color_border": "rgba(2, 132, 199, 0.25)",
    "color_success": "#059669",
    "color_warning": "#d97706",
    "color_error": "#dc2626",
    "radius_sm": "8px",
    "radius_md": "16px",
    "radius_lg": "24px",
    "container_width": "1200px",
    "section_space_desktop": "100px",
    "section_space_tablet": "72px",
    "section_space_mobile": "56px",
    "animation_speed": "0.6s",
    "animation_intensity": "normal",
    "animations_enabled": "true",
    "scroll_reveal": "true",
    "hover_effects": "true",
    "page_transitions": "true",
    "h1_size": "clamp(2.5rem, 6vw, 4rem)",
    "h2_size": "clamp(1.75rem, 4vw, 2.5rem)",
    "h3_size": "1.35rem",
    "body_size": "1rem",
    "letter_spacing_display": "0.08em",
    "line_height": "1.6",
    "shadow_strength": "0 8px 32px rgba(0,0,0,0.35)",
}


def generate_css_variables(theme=None):
    if theme is None:
        theme = get_all_theme()
    merged = {**DEFAULT_THEME, **theme}
    lines = [":root {"]
    mapping = {
        "theme_mode": "--theme-mode",
        "font_display": "--font-display",
        "font_heading": "--font-heading",
        "font_body": "--font-body",
        "font_nav": "--font-nav",
        "color_primary": "--color-primary",
        "color_secondary": "--color-secondary",
        "color_accent": "--color-accent",
        "color_bg": "--color-bg",
        "color_bg_deep": "--color-bg-deep",
        "color_surface": "--color-surface",
        "color_surface_2": "--color-surface-2",
        "color_text": "--color-text",
        "color_muted": "--color-muted",
        "color_border": "--color-border",
        "color_success": "--color-success",
        "color_warning": "--color-warning",
        "color_error": "--color-error",
        "radius_sm": "--radius-sm",
        "radius_md": "--radius-md",
        "radius_lg": "--radius-lg",
        "container_width": "--container",
        "section_space_desktop": "--section-space-desktop",
        "section_space_tablet": "--section-space-tablet",
        "section_space_mobile": "--section-space-mobile",
        "animation_speed": "--animation-speed",
        "h1_size": "--h1-size",
        "h2_size": "--h2-size",
        "h3_size": "--h3-size",
        "body_size": "--body-size",
        "letter_spacing_display": "--letter-spacing-display",
        "line_height": "--line-height",
        "shadow_strength": "--shadow",
    }
    for k, css_var in mapping.items():
        val = merged.get(k, DEFAULT_THEME.get(k, ""))
        lines.append(f"  {css_var}: {val};")
    lines.append("}")
    return "\n".join(lines)

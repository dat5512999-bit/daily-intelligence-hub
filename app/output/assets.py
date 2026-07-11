"""Static web assets emitted with the generated report."""

from __future__ import annotations

APP_ICON_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">
  <defs>
    <linearGradient id="bg" x1="68" y1="48" x2="456" y2="464" gradientUnits="userSpaceOnUse">
      <stop stop-color="#14f1ff"/>
      <stop offset="0.52" stop-color="#8f7cff"/>
      <stop offset="1" stop-color="#ff4f9a"/>
    </linearGradient>
    <radialGradient id="glow" cx="0" cy="0" r="1" gradientUnits="userSpaceOnUse"
                    gradientTransform="translate(342 144) rotate(121) scale(310)">
      <stop stop-color="#ffffff" stop-opacity="0.42"/>
      <stop offset="1" stop-color="#ffffff" stop-opacity="0"/>
    </radialGradient>
  </defs>
  <rect width="512" height="512" rx="112" fill="#0b0f19"/>
  <rect x="34" y="34" width="444" height="444" rx="94" fill="url(#bg)"/>
  <rect x="58" y="58" width="396" height="396" rx="78" fill="#101722"/>
  <rect x="58" y="58" width="396" height="396" rx="78" fill="url(#glow)"/>
  <circle cx="256" cy="256" r="142" fill="none" stroke="#ffffff" stroke-opacity="0.18" stroke-width="18"/>
  <circle cx="256" cy="256" r="82" fill="none" stroke="#ffffff" stroke-opacity="0.26" stroke-width="14"/>
  <path d="M256 256 L354 168" stroke="#14f1ff" stroke-width="22" stroke-linecap="round"/>
  <circle cx="256" cy="256" r="34" fill="#fff8ed"/>
  <circle cx="256" cy="256" r="15" fill="#101722"/>
  <path d="M169 342V166h92c56 0 91 31 91 78 0 31-16 55-44 67l54 31h-67l-47-27h-27v27h-52zm52-70h39c25 0 39-10 39-28s-14-28-39-28h-39z"
        fill="#fff8ed"/>
  <path d="M151 387h210" stroke="#ff4f9a" stroke-width="18" stroke-linecap="round"/>
</svg>
"""

WEB_MANIFEST = """{
  "name": "今天紅什麼情報雷達",
  "short_name": "今天紅什麼",
  "description": "個人每日趨勢、新聞、動漫、遊戲與持股情報雷達",
  "start_url": "./",
  "scope": "./",
  "display": "standalone",
  "background_color": "#101722",
  "theme_color": "#101722",
  "icons": [
    {
      "src": "app-icon.svg",
      "sizes": "any",
      "type": "image/svg+xml",
      "purpose": "any maskable"
    }
  ]
}
"""

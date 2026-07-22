import hashlib
import re

from django.conf import settings
from django.core.management.base import BaseCommand

from employees.models import Employee


class Command(BaseCommand):
    help = "Assign generated professional face avatars to employees."

    palettes = [
        ("#2563eb", "#93c5fd", "#172554"),
        ("#7c3aed", "#c4b5fd", "#2e1065"),
        ("#0891b2", "#67e8f9", "#164e63"),
        ("#16a34a", "#86efac", "#14532d"),
        ("#ea580c", "#fdba74", "#7c2d12"),
        ("#db2777", "#f9a8d4", "#831843"),
        ("#4f46e5", "#a5b4fc", "#1e1b4b"),
        ("#0f766e", "#5eead4", "#134e4a"),
    ]

    skin_tones = ["#f2c7a5", "#e8b88f", "#c98f68", "#9f6a4d", "#7a4c37"]
    hair_colors = ["#1f2937", "#3f2a20", "#111827", "#5c4033", "#2f241f"]

    def handle(self, *args, **options):
        target_dir = settings.MEDIA_ROOT / "employee_photos" / "generated"
        target_dir.mkdir(parents=True, exist_ok=True)

        updated = 0
        for employee in Employee.objects.order_by("id"):
            seed = int(hashlib.sha256(employee.name.encode("utf-8")).hexdigest(), 16)
            filename = f"{self._slug(employee.name)}-{employee.id}.svg"
            relative_path = f"employee_photos/generated/{filename}"
            output_path = target_dir / filename

            output_path.write_text(
                self._avatar_svg(employee.name, seed),
                encoding="utf-8",
            )

            if employee.photo.name != relative_path:
                employee.photo.name = relative_path
                employee.save(update_fields=["photo"])
                updated += 1

        self.stdout.write(self.style.SUCCESS(f"Assigned avatars to {updated} employees."))

    def _slug(self, value):
        slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
        return slug or "employee"

    def _avatar_svg(self, name, seed):
        palette = self.palettes[seed % len(self.palettes)]
        skin = self.skin_tones[(seed // 7) % len(self.skin_tones)]
        hair = self.hair_colors[(seed // 11) % len(self.hair_colors)]
        initials = "".join(part[0] for part in name.split()[:2]).upper() or "EM"
        smile = "M92 132 Q128 154 164 132" if seed % 2 else "M96 136 Q128 148 160 136"
        hair_shape = (
            "M62 98 C64 46 194 46 196 98 C180 78 154 68 128 68 C102 68 78 78 62 98Z"
            if seed % 3
            else "M58 104 C58 56 94 34 128 40 C168 34 198 60 198 104 C176 82 152 72 128 72 C103 72 78 82 58 104Z"
        )

        return f"""<svg xmlns="http://www.w3.org/2000/svg" width="256" height="256" viewBox="0 0 256 256" role="img" aria-label="{name} avatar">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="{palette[0]}"/>
      <stop offset="100%" stop-color="{palette[1]}"/>
    </linearGradient>
    <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="12" stdDeviation="10" flood-color="#020617" flood-opacity=".28"/>
    </filter>
  </defs>
  <rect width="256" height="256" rx="64" fill="url(#bg)"/>
  <circle cx="128" cy="132" r="82" fill="rgba(255,255,255,.16)"/>
  <g filter="url(#shadow)">
    <path d="{hair_shape}" fill="{hair}"/>
    <circle cx="128" cy="120" r="62" fill="{skin}"/>
    <path d="M72 112 C76 84 96 66 128 66 C160 66 181 84 185 112 C163 94 94 94 72 112Z" fill="{hair}"/>
    <circle cx="104" cy="121" r="6" fill="{palette[2]}"/>
    <circle cx="152" cy="121" r="6" fill="{palette[2]}"/>
    <path d="{smile}" fill="none" stroke="{palette[2]}" stroke-width="6" stroke-linecap="round"/>
    <path d="M85 204 C92 174 105 160 128 160 C151 160 164 174 171 204Z" fill="{palette[2]}" opacity=".9"/>
    <circle cx="128" cy="178" r="18" fill="{skin}"/>
  </g>
  <text x="128" y="232" text-anchor="middle" font-family="Arial, sans-serif" font-size="22" font-weight="700" fill="white" opacity=".92">{initials}</text>
</svg>
"""

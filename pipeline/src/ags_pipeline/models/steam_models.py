from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Optional, List, Dict, Any, Type, TypeVar
import datetime

T = TypeVar('T')


def _normalize_str(v: Any) -> Optional[str]:
    if v is None:
        return None
    if isinstance(v, str):
        return v
    try:
        return str(v)
    except Exception:
        return None


def _from_dict_list(cls: Type[T], data: Any) -> Optional[List[T]]:
    if data is None:
        return None
    if isinstance(data, list):
        out = []
        for it in data:
            if isinstance(it, dict):
                out.append(cls.from_dict(it))
            else:
                # attempt to coerce simple values
                out.append(cls.from_dict({'name': _normalize_str(it)}))
        return out
    return None


def _safe_int(v: Any) -> Optional[int]:
    try:
        if v is None:
            return None
        return int(v)
    except Exception:
        return None


def _safe_float(v: Any) -> Optional[float]:
    try:
        if v is None:
            return None
        return float(v)
    except Exception:
        return None


@dataclass
class PriceOverview:
    # final: normalized major-unit price (float) when possible
    final: Optional[float] = None
    # original/raw fields preserved for auditing
    raw_final: Any = None
    currency: Optional[str] = None
    raw_currency: Optional[str] = None
    # normalization metadata: 'exact', 'converted_by_currency', 'assumed', 'non_numeric', 'unknown'
    normalization_note: Optional[str] = None

    @classmethod
    def from_dict(cls, d: Optional[Dict[str, Any]]) -> Optional['PriceOverview']:
        if not d:
            return None
        raw_final = d.get('final')
        raw_currency = d.get('currency')
        currency = _normalize_str(raw_currency)

        # minor-unit mapping for many common ISO-4217 currencies.
        # If a currency is not present below we default to 2 (common case).
        minor_units = {
            'USD': 2, 'EUR': 2, 'GBP': 2, 'CAD': 2, 'AUD': 2, 'CNY': 2, 'RUB': 2,
            'JPY': 0, 'KRW': 0, 'VND': 0,
            'CHF': 2, 'SEK': 2, 'NOK': 2, 'DKK': 2, 'PLN': 2, 'CZK': 2, 'HUF': 2,
            'INR': 2, 'BRL': 2, 'MXN': 2, 'ARS': 2, 'CLP': 0, 'IDR': 2, 'TRY': 2,
            'ZAR': 2, 'SGD': 2, 'HKD': 2, 'TWD': 2, 'ILS': 2, 'AED': 2, 'SAR': 2,
            # Currencies with 3 minor units
            'KWD': 3, 'BHD': 3, 'OMR': 3, 'JOD': 3, 'TND': 3,
            # Common legacy or fractional cases
            'UYU': 2, 'PEN': 2, 'COP': 2, 'NZD': 2
        }

        normalized = None
        note = None
        # Integer handling: if currency known, use its minor unit mapping; otherwise defer to conservative fallback.
        if isinstance(raw_final, int):
            try:
                if currency:
                    mu = minor_units.get(currency.upper(), 2)
                    if mu == 0:
                        normalized = float(raw_final)
                        note = 'converted_by_currency_minor0'
                    else:
                        normalized = float(raw_final) / (10 ** mu)
                        note = 'converted_by_currency'
                else:
                    # currency unknown: conservative assumption later
                    normalized = None
                    note = None
            except Exception:
                normalized = None
                note = 'conversion_error'
        elif isinstance(raw_final, float):
            normalized = float(raw_final)
            note = 'float_presumed_major'
        else:
            # string or other: try to parse numeric from string
            if isinstance(raw_final, str):
                s = raw_final.strip()
                try:
                    # remove common non-numeric chars
                    s2 = s.replace('$','').replace(',','')
                    normalized = float(s2)
                    note = 'parsed_from_string'
                except Exception:
                    normalized = None
                    note = 'non_numeric_string'
            else:
                normalized = None
                note = 'unknown'

        # Conservative fallback: if currency missing and raw int looks like cents (>1000), assume cents
        if currency is None and normalized is None and isinstance(raw_final, int):
            if raw_final >= 1000:
                normalized = float(raw_final) / 100.0
                note = 'assumed_cents_no_currency'

        return cls(final=normalized, raw_final=raw_final, currency=currency, raw_currency=raw_currency, normalization_note=note)


@dataclass
class ReleaseDate:
    date: Optional[str] = None
    coming_soon: Optional[bool] = None

    @classmethod
    def from_dict(cls, d: Optional[Dict[str, Any]]) -> Optional['ReleaseDate']:
        if not d:
            return None
        date = d.get('date') if isinstance(d.get('date'), str) else None
        coming = d.get('coming_soon')
        if isinstance(coming, str):
            coming = coming.lower() in ('true', '1', 'yes')
        elif not isinstance(coming, bool):
            coming = None
        return cls(date=date, coming_soon=coming)


@dataclass
class SimpleNamed:
    id: Optional[int] = None
    name: Optional[str] = None
    description: Optional[str] = None

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> 'SimpleNamed':
        if not isinstance(d, dict):
            return cls(name=_normalize_str(d))
        return cls(id=d.get('id'), name=_normalize_str(d.get('name')), description=_normalize_str(d.get('description')))


@dataclass
class Requirements:
    minimum: Optional[str] = None
    recommended: Optional[str] = None

    @classmethod
    def from_dict(cls, d: Optional[Dict[str, Any]]) -> Optional['Requirements']:
        if not d:
            return None
        return cls(minimum=_normalize_str(d.get('minimum')), recommended=_normalize_str(d.get('recommended')))


@dataclass
class AppDetail:
    appid: Optional[int] = None
    name: Optional[str] = None
    short_description: Optional[str] = None
    detailed_description: Optional[str] = None
    price_overview: Optional[PriceOverview] = None
    release_date: Optional[ReleaseDate] = None
    categories: Optional[List[SimpleNamed]] = field(default_factory=list)
    genres: Optional[List[SimpleNamed]] = field(default_factory=list)
    developers: Optional[List[str]] = field(default_factory=list)
    publishers: Optional[List[str]] = field(default_factory=list)
    pc_requirements: Optional[Requirements] = None
    mac_requirements: Optional[Requirements] = None
    linux_requirements: Optional[Requirements] = None
    # Additional structured fields
    recommendations: Optional[int] = None
    achievements_count: Optional[int] = None
    metacritic_score: Optional[float] = None
    supported_languages: Optional[str] = None
    header_image: Optional[str] = None
    raw: Optional[Dict[str, Any]] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> 'AppDetail':
        if not isinstance(d, dict):
            raise ValueError('from_dict expects a dict')

        price = PriceOverview.from_dict(d.get('price_overview'))
        release = ReleaseDate.from_dict(d.get('release_date'))
        cats = _from_dict_list(SimpleNamed, d.get('categories')) or []
        gens = _from_dict_list(SimpleNamed, d.get('genres')) or []
        devs = d.get('developers') if isinstance(d.get('developers'), list) else ([d.get('developers')] if d.get('developers') else [])
        pubs = d.get('publishers') if isinstance(d.get('publishers'), list) else ([d.get('publishers')] if d.get('publishers') else [])
        pcreq = Requirements.from_dict(d.get('pc_requirements'))
        macreq = Requirements.from_dict(d.get('mac_requirements'))
        linreq = Requirements.from_dict(d.get('linux_requirements'))

        # Preserve any remaining unknown fields into `raw` for later inspection
        known = {
            'appid','name','short_description','detailed_description','price_overview',
            'release_date','categories','genres','developers','publishers',
            'pc_requirements','mac_requirements','linux_requirements'
        }
        raw = {k: v for k, v in d.items() if k not in known}

        # Recommendations may be nested e.g. {'total': 1234}
        rec = d.get('recommendations')
        rec_total = _safe_int(rec.get('total')) if isinstance(rec, dict) else _safe_int(rec)

        # Achievements count often appears under 'achievements' -> 'total'
        ach = d.get('achievements')
        ach_total = _safe_int(ach.get('total')) if isinstance(ach, dict) else None

        # Metacritic score
        mc = d.get('metacritic')
        mc_score = _safe_float(mc.get('score')) if isinstance(mc, dict) else None

        supported_languages = _normalize_str(d.get('supported_languages'))
        header_image = _normalize_str(d.get('header_image'))

        return cls(
            appid=d.get('steam_appid') or d.get('appid') or d.get('app_id') or d.get('id'),
            name=_normalize_str(d.get('name')),
            short_description=_normalize_str(d.get('short_description') or d.get('shortdesc') or d.get('short_desc')),
            detailed_description=_normalize_str(d.get('detailed_description') or d.get('detailed_desc') or d.get('detailedDescription')),
            price_overview=price,
            release_date=release,
            categories=cats,
            genres=gens,
            developers=[_normalize_str(x) for x in (devs or []) if x],
            publishers=[_normalize_str(x) for x in (pubs or []) if x],
            pc_requirements=pcreq,
            mac_requirements=macreq,
            linux_requirements=linreq,
            recommendations=rec_total,
            achievements_count=ach_total,
            metacritic_score=mc_score,
            supported_languages=supported_languages,
            header_image=header_image,
            raw=raw
        )

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        # convert dataclasses inside to serializable dicts
        if self.price_overview:
            d['price_overview'] = asdict(self.price_overview)
        if self.release_date:
            d['release_date'] = asdict(self.release_date)
        if self.pc_requirements:
            d['pc_requirements'] = asdict(self.pc_requirements)
        if self.mac_requirements:
            d['mac_requirements'] = asdict(self.mac_requirements)
        if self.linux_requirements:
            d['linux_requirements'] = asdict(self.linux_requirements)
        # SimpleNamed items -> dict
        d['categories'] = [asdict(x) for x in (self.categories or [])]
        d['genres'] = [asdict(x) for x in (self.genres or [])]
        return d

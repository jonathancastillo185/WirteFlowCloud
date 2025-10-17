"""
Perfiles y dimensiones de estilo predefinidos para diferentes tipos de narrativa.
"""

from typing import Dict, List, Any

# ============================================================================
# DIMENSIONES DE ESCRITURA
# ============================================================================

WRITING_DIMENSIONS = {
    "prose_complexity": {
        "simple": {
            "name": "Simple y Directa",
            "description": "Oraciones cortas, vocabulario accesible, sin florituras",
            "characteristics": [
                "Oraciones de 10-15 palabras en promedio",
                "Vocabulario cotidiano",
                "Estructura sujeto-verbo-objeto",
                "Evita metáforas complejas"
            ]
        },
        "moderate": {
            "name": "Balanceada",
            "description": "Mezcla de claridad y elaboración literaria",
            "characteristics": [
                "Oraciones variadas en longitud",
                "Vocabulario enriquecido pero comprensible",
                "Algunas metáforas y figuras retóricas",
                "Balance entre mostrar y contar"
            ]
        },
        "complex": {
            "name": "Compleja y Literaria",
            "description": "Prosa elaborada con profundidad estilística",
            "characteristics": [
                "Oraciones largas y subordinadas",
                "Vocabulario sofisticado",
                "Metáforas elaboradas y simbolismo",
                "Múltiples capas de significado"
            ]
        },
        "experimental": {
            "name": "Experimental",
            "description": "Experimentación lingüística y narrativa",
            "characteristics": [
                "Estructura narrativa no lineal",
                "Juegos de lenguaje y neologismos",
                "Ruptura de convenciones",
                "Prosa poética o fragmentada"
            ]
        }
    },
    
    "narrative_density": {
        "fast_paced": {
            "name": "Ritmo Rápido",
            "description": "Acción constante, cambios frecuentes de escena",
            "characteristics": [
                "Escenas cortas y dinámicas",
                "Transiciones rápidas",
                "Mínimo tiempo muerto",
                "Enfoque en eventos externos"
            ]
        },
        "balanced": {
            "name": "Equilibrado",
            "description": "Alterna entre acción y reflexión",
            "characteristics": [
                "Mezcla de escenas de acción e introspección",
                "Ritmo variable según necesidades de la trama",
                "Balance entre externo e interno",
                "Pausas estratégicas"
            ]
        },
        "contemplative": {
            "name": "Contemplativo",
            "description": "Énfasis en reflexión y atmósfera",
            "characteristics": [
                "Escenas largas y detalladas",
                "Énfasis en estados internos",
                "Desarrollo atmosférico",
                "Tiempo para la introspección"
            ]
        },
        "epic": {
            "name": "Épico",
            "description": "Narrativa expansiva con múltiples líneas argumentales",
            "characteristics": [
                "Múltiples puntos de vista",
                "Tramas paralelas complejas",
                "Worldbuilding extenso",
                "Escala temporal amplia"
            ]
        }
    },
    
    "description_level": {
        "minimal": {
            "name": "Minimalista",
            "description": "Solo detalles esenciales para la trama",
            "characteristics": [
                "Descripciones funcionales únicamente",
                "Máximo 2-3 líneas por escenario",
                "Sin detalles sensoriales elaborados",
                "Prioridad absoluta a la acción"
            ]
        },
        "selective": {
            "name": "Selectiva",
            "description": "Descripciones estratégicas en momentos clave",
            "characteristics": [
                "Descripciones cuando aportan a la atmósfera",
                "Detalles significativos para la trama",
                "Balance entre mostrar y avanzar",
                "Énfasis en lo visualmente impactante"
            ]
        },
        "rich": {
            "name": "Rica",
            "description": "Descripciones detalladas y evocadoras",
            "characteristics": [
                "Detalles sensoriales completos",
                "Descripciones de 1-2 párrafos",
                "Énfasis en atmósfera y mood",
                "Worldbuilding integrado"
            ]
        },
        "immersive": {
            "name": "Inmersiva",
            "description": "Experiencia sensorial completa",
            "characteristics": [
                "Todos los sentidos representados",
                "Descripciones extensas y poéticas",
                "Construcción de mundo detallada",
                "El escenario como personaje"
            ]
        }
    },
    
    "thematic_depth": {
        "entertainment": {
            "name": "Entretenimiento",
            "description": "Enfoque principal en la trama y el disfrute",
            "characteristics": [
                "Los temas sirven a la historia",
                "Mensajes claros y directos",
                "Sin ambigüedad moral compleja",
                "Resoluciones satisfactorias"
            ]
        },
        "layered": {
            "name": "Por Capas",
            "description": "Temas sutiles entretejidos en la narrativa",
            "characteristics": [
                "Subtexto presente pero no dominante",
                "Temas se revelan gradualmente",
                "Simbolismo moderado",
                "Interpretaciones múltiples posibles"
            ]
        },
        "philosophical": {
            "name": "Filosófico",
            "description": "Exploración profunda de ideas y conceptos",
            "characteristics": [
                "Temas filosóficos centrales",
                "Dilemas morales complejos",
                "Cuestionamiento existencial",
                "Sin respuestas fáciles"
            ]
        },
        "deconstructive": {
            "name": "Deconstructivo",
            "description": "Deconstrucción de géneros y expectativas",
            "characteristics": [
                "Subversión de tropos",
                "Meta-narrativa",
                "Ambigüedad intencional",
                "Desafío al lector"
            ]
        }
    },
    
    "dialogue_style": {
        "functional": {
            "name": "Funcional",
            "description": "Diálogos directos que avanzan la trama",
            "characteristics": [
                "Intercambios breves",
                "Información clara y directa",
                "Sin subtexto complejo",
                "Enfoque en avanzar la historia"
            ]
        },
        "natural": {
            "name": "Natural",
            "description": "Diálogos realistas con subtexto",
            "characteristics": [
                "Conversaciones orgánicas",
                "Incluye pausas y evasivas",
                "Subtexto moderado",
                "Revela personalidad"
            ]
        },
        "stylized": {
            "name": "Estilizado",
            "description": "Diálogos con personalidad literaria fuerte",
            "characteristics": [
                "Voces muy distintivas",
                "Puede ser más elaborado que el habla real",
                "Sirve al tono de la obra",
                "Memorablemente único"
            ]
        },
        "poetic": {
            "name": "Poético",
            "description": "Diálogos como arte verbal",
            "characteristics": [
                "Alta elaboración lingüística",
                "Metáforas en el habla",
                "Ritmo y musicalidad",
                "Puede sacrificar realismo por belleza"
            ]
        }
    }
}

# ============================================================================
# PERFILES PREDEFINIDOS
# ============================================================================

STYLE_PRESETS = {
    # ------------------------------------------------------------------------
    # PERFIL: EVANGELION - Ciencia ficción psicológica compleja
    # ------------------------------------------------------------------------
    "evangelion_balanced": {
        "name": "Evangelion Balanceado - Complejo pero Legible",
        "description": "Mantiene la profundidad psicológica pero con mejor ritmo",
        "dimensions": {
            "prose_complexity": "moderate",
            "narrative_density": "balanced",
            "description_level": "selective",
            "thematic_depth": "philosophical",
            "dialogue_style": "natural"
        },
        "special_instructions": [
            "Simbolismo presente pero no dominante",
            "Monólogos internos breves y poderosos",
            "Balance entre introspección y acción",
            "Claridad sin sacrificar profundidad",
            "Primeros párrafos siempre concretos"
        ]
    },
    "evangelion": {
        "name": "Evangelion - Psicológico Complejo",
        "description": "Narrativa densa con simbolismo religioso, exploración psicológica profunda y ambigüedad intencional",
        "dimensions": {
        "prose_complexity": "complex",
        "narrative_density": "balanced",
        "description_level": "rich",
        "thematic_depth": "philosophical",
        "dialogue_style": "stylized"
        },
        "special_instructions": [
            "Permite y fomenta el simbolismo religioso y filosófico",
            "Los monólogos internos pueden ser extensos y fragmentados",
            "La ambigüedad narrativa es una característica, no un error",
            "Explora la psicología de los personajes en profundidad",
            "Las escenas pueden tener múltiples capas de interpretación",
            "El silencio y las pausas son significativos",
            "No temas dejar preguntas sin responder inmediata"
        ],
        "avoid": [
            "Resoluciones simplistas de conflictos psicológicos",
            "Explicaciones directas de simbolismo",
            "Ritmo uniformemente rápido"
        ],
        "examples": [
            "Correcto: 'El mar rojo se extendía ante él, infinito como su culpa. O quizás era el cielo. Ya no podía distinguir dónde terminaba uno y empezaba el otro.'",
            "Incorrecto: 'Miró el mar rojo y se sintió culpable por lo que había hecho.'"
        ]
    },
    
    # ------------------------------------------------------------------------
    # PERFIL: THRILLER RÁPIDO
    # ------------------------------------------------------------------------
    "thriller_fast": {
        "name": "Thriller de Acción Rápida",
        "description": "Narrativa ágil enfocada en acción constante y tensión",
        "dimensions": {
            "prose_complexity": "simple",
            "narrative_density": "fast_paced",
            "description_level": "minimal",
            "thematic_depth": "entertainment",
            "dialogue_style": "functional"
        },
        "special_instructions": [
            "Cada escena debe avanzar la trama",
            "Oraciones cortas en momentos de acción",
            "Descripciones solo de elementos relevantes para la acción",
            "Capítulos cortos con cliffhangers",
            "Ritmo constante y creciente",
            "Diálogos concisos y con propósito"
        ],
        "avoid": [
            "Descripciones atmosféricas largas",
            "Introspección extensa",
            "Escenas sin conflicto directo"
        ],
        "examples": [
            "Correcto: 'Corrió. La puerta estaba a veinte metros. Quince. Los pasos se acercaban detrás.'",
            "Incorrecto: 'Corrió por el pasillo, cuyas paredes de un blanco impoluto reflejaban la luz fluorescente que parpadeaba suavemente...'"
        ]
    },
    
    # ------------------------------------------------------------------------
    # PERFIL: FANTASÍA ÉPICA
    # ------------------------------------------------------------------------
    "fantasy_epic": {
        "name": "Fantasía Épica",
        "description": "Worldbuilding rico con múltiples tramas y escala épica",
        "dimensions": {
            "prose_complexity": "moderate",
            "narrative_density": "epic",
            "description_level": "rich",
            "thematic_depth": "layered",
            "dialogue_style": "stylized"
        },
        "special_instructions": [
            "Dedica espacio al worldbuilding y la historia del mundo",
            "Múltiples puntos de vista son bienvenidos",
            "Las descripciones de lugares son importantes",
            "Los sistemas de magia/poder deben ser consistentes",
            "Permite tramas paralelas complejas",
            "El tono puede ser elevado y formal cuando sea apropiado"
        ],
        "avoid": [
            "Ritmo uniformemente rápido sin pausas",
            "Worldbuilding superficial",
            "Resoluciones fáciles de conflictos mayores"
        ],
        "examples": [
            "Correcto: 'Las Torres de Cristal se alzaban sobre el Valle de Ámbar, testigos mudos de mil años de magia olvidada.'",
            "Incorrecto: 'Había unas torres de cristal en el valle.'"
        ]
    },
    
    # ------------------------------------------------------------------------
    # PERFIL: ROMANCE CONTEMPORÁNEO
    # ------------------------------------------------------------------------
    "romance_contemporary": {
        "name": "Romance Contemporáneo",
        "description": "Enfoque en desarrollo de relaciones y emociones",
        "dimensions": {
            "prose_complexity": "moderate",
            "narrative_density": "balanced",
            "description_level": "selective",
            "thematic_depth": "layered",
            "dialogue_style": "natural"
        },
        "special_instructions": [
            "Los diálogos entre protagonistas son el corazón de la historia",
            "Permite momentos íntimos y de desarrollo emocional",
            "Las descripciones deben capturar mood y atmósfera romántica",
            "La tensión emocional es tan importante como la física",
            "Los conflictos internos son válidos y necesarios"
        ],
        "avoid": [
            "Resolución instantánea de conflictos emocionales",
            "Diálogos puramente funcionales en escenas románticas",
            "Falta de subtexto emocional"
        ]
    },
    
    # ------------------------------------------------------------------------
    # PERFIL: HORROR ATMOSFÉRICO
    # ------------------------------------------------------------------------
    "horror_atmospheric": {
        "name": "Horror Atmosférico",
        "description": "Terror psicológico basado en atmósfera y tensión",
        "dimensions": {
            "prose_complexity": "complex",
            "narrative_density": "contemplative",
            "description_level": "immersive",
            "thematic_depth": "philosophical",
            "dialogue_style": "natural"
        },
        "special_instructions": [
            "La atmósfera es fundamental - dedica espacio a construirla",
            "Lo no dicho es tan importante como lo dicho",
            "Descripciones sensoriales detalladas (sonidos, olores, texturas)",
            "El horror puede ser sugerido en lugar de explícito",
            "Permite que la tensión se construya lentamente",
            "Los espacios y el ambiente son casi personajes"
        ],
        "avoid": [
            "Horror explícito constante",
            "Explicaciones racionales inmediatas",
            "Ritmo demasiado rápido que no permite tensión"
        ]
    },
    
    # ------------------------------------------------------------------------
    # PERFIL: LITERARIO EXPERIMENTAL
    # ------------------------------------------------------------------------
    "literary_experimental": {
        "name": "Ficción Literaria Experimental",
        "description": "Experimentación narrativa y estilística",
        "dimensions": {
            "prose_complexity": "experimental",
            "narrative_density": "contemplative",
            "description_level": "immersive",
            "thematic_depth": "deconstructive",
            "dialogue_style": "poetic"
        },
        "special_instructions": [
            "Se alienta la experimentación con estructura narrativa",
            "La prosa puede ser poética y no convencional",
            "Permite flujo de consciencia y narrativa fragmentada",
            "Los temas pueden ser abstractos y filosóficos",
            "No todas las preguntas necesitan respuesta",
            "El estilo es tan importante como la historia"
        ],
        "avoid": [
            "Convenciones narrativas rígidas",
            "Resoluciones tradicionales",
            "Claridad por sobre expresión artística"
        ]
    },
    
    # ------------------------------------------------------------------------
    # PERFIL: MISTERIO CLÁSICO
    # ------------------------------------------------------------------------
    "mystery_classic": {
        "name": "Misterio Clásico",
        "description": "Enigma estructurado con pistas y revelaciones",
        "dimensions": {
            "prose_complexity": "moderate",
            "narrative_density": "balanced",
            "description_level": "selective",
            "thematic_depth": "entertainment",
            "dialogue_style": "natural"
        },
        "special_instructions": [
            "Las pistas deben estar presentes pero no ser obvias",
            "Cada capítulo debe revelar o complicar el misterio",
            "Los diálogos de interrogatorio son momentos clave",
            "La lógica deductiva debe ser sólida",
            "Permite red herrings y giros sorpresivos"
        ],
        "avoid": [
            "Pistas que aparecen solo al final",
            "Resoluciones basadas en información no presentada",
            "Detectivismo sin proceso lógico"
        ]
    },
    
    # ------------------------------------------------------------------------
    # PERFIL: CIENCIA FICCIÓN HARD
    # ------------------------------------------------------------------------
    "scifi_hard": {
        "name": "Ciencia Ficción Hard",
        "description": "Ciencia ficción con rigor científico y técnico",
        "dimensions": {
            "prose_complexity": "moderate",
            "narrative_density": "balanced",
            "description_level": "rich",
            "thematic_depth": "philosophical",
            "dialogue_style": "natural"
        },
        "special_instructions": [
            "Los conceptos científicos deben ser coherentes y bien desarrollados",
            "Permite explicaciones técnicas cuando sean relevantes",
            "La especulación debe estar fundamentada",
            "Los problemas se resuelven con lógica y ciencia",
            "El worldbuilding sigue reglas científicas establecidas"
        ],
        "avoid": [
            "Tecnología mágica sin explicación",
            "Violaciones de las propias reglas científicas establecidas",
            "Simplicidad excesiva en conceptos complejos"
        ]
    }
}

# ============================================================================
# PERFIL POR DEFECTO
# ============================================================================

DEFAULT_PROFILE = "balanced_neutral"

STYLE_PRESETS["balanced_neutral"] = {
    "name": "Balanceado y Neutral",
    "description": "Estilo versátil que se adapta a la historia sin imponer características extremas",
    "dimensions": {
        "prose_complexity": "moderate",
        "narrative_density": "balanced",
        "description_level": "selective",
        "thematic_depth": "layered",
        "dialogue_style": "natural"
    },
    "special_instructions": [
        "Adapta el estilo según las necesidades de cada escena",
        "Balance entre mostrar y contar",
        "Claridad sin sacrificar profundidad",
        "Ritmo variable según el contexto"
    ],
    "avoid": []
}

# ============================================================================
# FUNCIONES AUXILIARES
# ============================================================================

def get_profile_names() -> List[str]:
    """Retorna lista de nombres de perfiles disponibles."""
    return list(STYLE_PRESETS.keys())

def get_profile_info(profile_name: str) -> Dict[str, Any]:
    """Retorna información completa de un perfil."""
    if profile_name not in STYLE_PRESETS:
        return STYLE_PRESETS[DEFAULT_PROFILE]
    return STYLE_PRESETS[profile_name]

def get_dimension_info(dimension: str, level: str) -> Dict[str, Any]:
    """Retorna información de una dimensión específica."""
    if dimension not in WRITING_DIMENSIONS:
        return {}
    if level not in WRITING_DIMENSIONS[dimension]:
        return {}
    return WRITING_DIMENSIONS[dimension][level]
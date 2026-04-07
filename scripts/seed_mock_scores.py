"""Seed mock scores, content angles, and pipeline run for dashboard testing."""

from datetime import date, datetime, timezone
from decimal import Decimal
from uuid import uuid4

from services.shared.config import get_settings
from services.shared.db.session import build_session_factory
from services.shared.db.models import (
    Product,
    ProductScore,
    ContentAngle,
    PipelineRun,
)


def main() -> None:
    sf = build_session_factory(settings=get_settings())
    now = datetime.now(timezone.utc)
    week_start = date(2026, 3, 16)

    with sf() as s:
        existing = s.query(ProductScore).count()
        if existing > 0:
            print(f"Already have {existing} scores, skipping seed")
            return

        # Pipeline run
        run = PipelineRun(
            id=str(uuid4()),
            week_start=week_start,
            status="completed",
            started_at=now,
            finished_at=now,
            input_job_ids=[],
            config_version="seed-v1",
        )
        s.add(run)

        products = s.query(Product).all()
        if len(products) < 3:
            print(f"Need at least 3 products, found {len(products)}. Run ingest-mock first.")
            return

        mock_scores = [
            {
                "trend_score": Decimal("82.50"),
                "viral_potential_score": Decimal("76.30"),
                "creator_accessibility_score": Decimal("68.00"),
                "saturation_penalty": Decimal("3.20"),
                "revenue_estimate": Decimal("245.00"),
                "final_score": Decimal("87.40"),
                "classification": "EXPLOSIVE",
                "explainability_payload": {
                    "summary": "Produto com forte momentum de tendencia e alto potencial viral. Ideal para criadores de conteudo de nicho de cozinha.",
                    "positive_signals": [
                        "Crescimento de views de 340% nos ultimos 7 dias",
                        "Taxa de engajamento acima da media do nicho",
                        "Comissao atrativa de 15%",
                    ],
                    "negative_signals": [
                        "Preco pode ser barreira para publico jovem",
                    ],
                    "risk_flags": ["short_history"],
                    "agent_reasoning": {
                        "trend": {
                            "strengths": ["Google Trends score em 85/100", "Crescimento exponencial de buscas"],
                            "weaknesses": ["Pode ser sazonal"],
                            "evidence": ["Google Trends data mostra pico em marco 2026"],
                        },
                        "viral": {
                            "strengths": ["Produto visual - perfeito para demonstracoes", "Hook claro: antes/depois"],
                            "weaknesses": ["Necessita boa iluminacao para demo"],
                            "evidence": ["Videos similares com media de 500K views"],
                        },
                        "accessibility": {
                            "strengths": ["Poucos criadores grandes no nicho", "Facil de demonstrar em casa"],
                            "weaknesses": ["Necessita produto em maos para review"],
                            "evidence": ["Apenas 23 criadores ativos neste produto"],
                        },
                    },
                },
            },
            {
                "trend_score": Decimal("65.00"),
                "viral_potential_score": Decimal("89.10"),
                "creator_accessibility_score": Decimal("72.50"),
                "saturation_penalty": Decimal("8.50"),
                "revenue_estimate": Decimal("180.00"),
                "final_score": Decimal("74.20"),
                "classification": "HIGH",
                "explainability_payload": {
                    "summary": "Alto potencial viral com demos de transformacao. Saturacao media requer angulos criativos.",
                    "positive_signals": [
                        "Potencial viral excepcional - visual transformation hook",
                        "Nicho de beleza com alta conversao",
                    ],
                    "negative_signals": [
                        "Saturacao media - muitos criadores ja promovendo",
                        "Necessita demonstracao pessoal",
                    ],
                    "risk_flags": ["high_saturation", "price_volatility"],
                    "agent_reasoning": {
                        "trend": {
                            "strengths": ["Trending em beleza/cuidados"],
                            "weaknesses": ["Concorrencia alta no nicho"],
                            "evidence": ["Hashtag #heatlesscurls com 2B views"],
                        },
                        "viral": {
                            "strengths": ["Transformacao visual perfeita para TikTok", "Hook de antes/depois fortissimo"],
                            "weaknesses": [],
                            "evidence": ["Top videos com 2M+ views"],
                        },
                        "accessibility": {
                            "strengths": ["Facil de usar em casa", "Resultado visual imediato"],
                            "weaknesses": ["Muitos criadores ja dominam o nicho"],
                            "evidence": ["142 criadores ativos - saturacao media"],
                        },
                    },
                },
            },
            {
                "trend_score": Decimal("45.00"),
                "viral_potential_score": Decimal("52.00"),
                "creator_accessibility_score": Decimal("85.00"),
                "saturation_penalty": Decimal("1.50"),
                "revenue_estimate": Decimal("95.00"),
                "final_score": Decimal("58.30"),
                "classification": "WORTH_TEST",
                "explainability_payload": {
                    "summary": "Nicho pouco explorado com boa acessibilidade. Tendencia moderada mas baixa saturacao.",
                    "positive_signals": [
                        "Saturacao muito baixa - oportunidade de ser primeiro",
                        "Alta acessibilidade para criadores",
                    ],
                    "negative_signals": [
                        "Tendencia moderada - mercado ainda pequeno",
                        "Revenue estimate abaixo da media",
                    ],
                    "risk_flags": ["weak_evidence"],
                    "agent_reasoning": {
                        "trend": {
                            "strengths": ["Crescimento estavel"],
                            "weaknesses": ["Mercado pequeno ainda", "Tendencia nao confirmada"],
                            "evidence": ["Google Trends score: 45/100"],
                        },
                        "viral": {
                            "strengths": ["Demonstracao com pets = alto engajamento"],
                            "weaknesses": ["Dificil controlar resultado com animais"],
                            "evidence": ["Videos com pets tem 2x mais engajamento"],
                        },
                        "accessibility": {
                            "strengths": ["Apenas 8 criadores ativos", "Baixissima concorrencia"],
                            "weaknesses": [],
                            "evidence": ["Nicho praticamente virgem para TikTok Shop"],
                        },
                    },
                },
            },
        ]

        for i, prod in enumerate(products[:3]):
            ms = mock_scores[i]
            score = ProductScore(
                id=str(uuid4()),
                product_id=prod.id,
                run_id=run.id,
                week_start=week_start,
                trend_score=ms["trend_score"],
                viral_potential_score=ms["viral_potential_score"],
                creator_accessibility_score=ms["creator_accessibility_score"],
                saturation_penalty=ms["saturation_penalty"],
                revenue_estimate=ms["revenue_estimate"],
                final_score=ms["final_score"],
                classification=ms["classification"],
                explainability_payload=ms["explainability_payload"],
                created_at=now,
            )
            s.add(score)

        # Content angles
        angle_data = [
            (products[0].id, "momentum_hook",
             "Esse liquidificador portatil carrega por USB e faz smoothie em 30 segundos - e cabe na bolsa!",
             "Produto com forte apelo visual e demonstracao rapida, ideal para hook de momentum."),
            (products[0].id, "problem_solution",
             "Cansado de lavar liquidificador gigante so pra um copo de suco? Descobri a solucao perfeita.",
             "Angulo de dor cotidiana com solucao imediata - alta conversao em nicho de cozinha."),
            (products[1].id, "transformation",
             "Fui dormir com cabelo liso e acordei com cachos PERFEITOS sem usar calor - olha isso!",
             "Transformacao visual antes/depois e hook fortissimo para TikTok."),
            (products[1].id, "social_proof",
             "3 milhoes de mulheres ja testaram esse metodo de cachos sem calor. Veja porque funciona.",
             "Prova social com numero expressivo para gerar autoridade."),
            (products[2].id, "curiosity_gap",
             "Meu gato ODIAVA ser escovado ate eu descobrir esse rolo magico. A reacao dele foi surreal.",
             "Curiosidade + pets = engajamento garantido. Hook que prende nos primeiros 2 segundos."),
        ]

        for pid, atype, hook, rationale in angle_data:
            angle = ContentAngle(
                id=str(uuid4()),
                product_id=pid,
                run_id=run.id,
                week_start=week_start,
                angle_type=atype,
                hook_text=hook,
                supporting_rationale=rationale,
                created_at=now,
            )
            s.add(angle)

        s.commit()
        print("Seeded: 1 pipeline run, 3 scores, 5 content angles")

    with sf() as s:
        print(f"Total scores: {s.query(ProductScore).count()}")
        print(f"Total angles: {s.query(ContentAngle).count()}")
        print(f"Total runs: {s.query(PipelineRun).count()}")


if __name__ == "__main__":
    main()

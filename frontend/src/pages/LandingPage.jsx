import React from "react";
import { Link, useNavigate } from "react-router-dom";

export function LandingPage() {
  const navigate = useNavigate();

  return (
    <div className="bg-background-light dark:bg-background-dark font-body text-text-main dark:text-gray-100 selection:bg-primary/10 selection:text-primary overflow-x-hidden min-h-screen">
      {/* TopAppBar */}
      <header className="fixed top-0 w-full z-50 bg-surface/80 dark:bg-surface-dark/80 backdrop-blur-xl shadow-sm dark:shadow-none">
        <nav className="flex justify-between items-center max-w-7xl mx-auto px-6 h-16">
          <div className="text-2xl font-black tracking-tighter text-primary">
            Radar
          </div>
          <div className="hidden md:flex items-center gap-8">
            <a
              className="text-primary font-bold border-b-2 border-primary pb-1"
              href="#radar"
            >
              Radar
            </a>
            <a
              className="text-muted font-medium hover:text-primary transition-colors"
              href="#raiox"
            >
              Raio-X
            </a>
            <a
              className="text-muted font-medium hover:text-primary transition-colors"
              href="#lab"
            >
              Laboratório
            </a>
            <a
              className="text-muted font-medium hover:text-primary transition-colors"
              href="#precos"
            >
              Preços
            </a>
          </div>
          <div className="flex items-center gap-4">
            <button
              onClick={() => navigate("/login")}
              className="hidden md:block text-muted font-medium hover:text-primary transition-colors"
            >
              Entrar
            </button>
            <button
              onClick={() => navigate("/login")}
              className="bg-primary text-white px-6 py-2.5 rounded-lg font-bold hover:scale-105 transition-transform duration-200 shadow-md"
            >
              Começar Agora
            </button>
          </div>
        </nav>
      </header>

      <main className="pt-16">
        {/* Hero Section */}
        <section className="relative min-h-[921px] flex items-center justify-center px-6 pulse-bg overflow-hidden">
          <div className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <div className="space-y-8 relative z-10">
              <div className="inline-flex items-center gap-2 bg-primary/10 text-primary px-3 py-1 rounded-md text-sm font-bold uppercase tracking-wider">
                <span
                  className="material-symbols-outlined text-sm"
                  style={{ fontVariationSettings: "'FILL' 1" }}
                >
                  bolt
                </span>
                Estúdio do Criador Elite
              </div>
              <h1 className="text-5xl md:text-7xl font-black tracking-tighter leading-tight text-text-main dark:text-gray-100">
                Domine o TikTok Shop com{" "}
                <span className="text-primary italic">Dados</span>, Não Sorte.
              </h1>
              <p className="text-xl text-muted max-w-lg leading-relaxed">
                A única inteligência competitiva desenhada para afiliados que
                buscam escala real. Identifique tendências antes que saturem e
                replique os ângulos que vendem.
              </p>
              <div className="flex flex-col sm:flex-row gap-4 pt-4">
                <button
                  onClick={() => navigate("/login")}
                  className="bg-primary text-white px-8 py-4 rounded-xl font-black text-lg hover:scale-105 transition-all shadow-lg flex items-center justify-center gap-2"
                >
                  Começar Agora
                  <span className="material-symbols-outlined">
                    arrow_forward
                  </span>
                </button>
                <button className="bg-background-light/50 dark:bg-surface-dark/50 backdrop-blur-md text-text-main dark:text-white px-8 py-4 rounded-xl font-bold text-lg hover:bg-background-light dark:bg-surface-dark transition-all border border-outline flex items-center justify-center gap-2">
                  Ver Demonstração
                  <span className="material-symbols-outlined">play_circle</span>
                </button>
              </div>
            </div>
            <div className="relative lg:block hidden">
              <div className="absolute -top-20 -right-20 w-64 h-64 bg-accent/10 rounded-full blur-3xl"></div>
              <div className="absolute -bottom-20 -left-20 w-64 h-64 bg-primary/10 rounded-full blur-3xl"></div>
              <div className="relative p-2 rounded-2xl bg-gradient-to-br from-primary via-secondary to-tertiary p-[2px]">
                <div className="bg-surface rounded-2xl p-6 shadow-2xl space-y-6">
                  <div className="flex justify-between items-center border-b border-outline pb-4">
                    <div className="flex gap-2 items-center">
                      <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center text-primary">
                        <span className="material-symbols-outlined">
                          trending_up
                        </span>
                      </div>
                      <div>
                        <p className="text-xs font-bold text-muted uppercase">
                          Tendência Semanal
                        </p>
                        <p className="font-black text-lg">Cremes Coreanos</p>
                      </div>
                    </div>
                    <div className="bg-success/10 text-success px-3 py-1 rounded-md text-xs font-black">
                      +124% ALTA
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="bg-background-light dark:bg-background-dark p-4 rounded-xl">
                      <p className="text-[10px] font-bold text-muted uppercase">
                        Conversão Média
                      </p>
                      <p className="text-2xl font-black text-text-main dark:text-white">
                        4.2%
                      </p>
                    </div>
                    <div className="bg-background-light dark:bg-background-dark p-4 rounded-xl">
                      <p className="text-[10px] font-bold text-muted uppercase">
                        Comissão Estimada
                      </p>
                      <p className="text-2xl font-black text-success">
                        R$ 12k+
                      </p>
                    </div>
                  </div>
                  <div className="relative h-32 w-full bg-surface dark:bg-surface-dark rounded-xl overflow-hidden flex items-end px-2 gap-1">
                    <div className="w-full bg-primary h-[30%] rounded-t-sm opacity-20"></div>
                    <div className="w-full bg-primary h-[45%] rounded-t-sm opacity-40"></div>
                    <div className="w-full bg-primary h-[40%] rounded-t-sm opacity-60"></div>
                    <div className="w-full bg-primary h-[70%] rounded-t-sm opacity-80"></div>
                    <div className="w-full bg-primary h-[90%] rounded-t-sm"></div>
                    <div className="w-full bg-primary h-[85%] rounded-t-sm"></div>
                    <div className="w-full bg-primary h-[95%] rounded-t-sm"></div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Problem Section */}
        <section
          id="radar"
          className="py-24 px-6 bg-background-light dark:bg-background-dark"
        >
          <div className="max-w-7xl mx-auto">
            <div className="max-w-3xl mb-16">
              <h2 className="text-4xl md:text-5xl font-black tracking-tighter mb-6">
                O problema de ser um afiliado hoje
              </h2>
              <p className="text-lg text-muted">
                Vender no TikTok Shop parece fácil, mas o mercado amador está
                sendo varrido por quem tem as ferramentas certas.
              </p>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              <div className="group bg-surface p-8 rounded-2xl shadow-sm hover:shadow-lg transition-all hover:-translate-y-2 border-transparent hover:border-outline-variant border-2">
                <div className="w-14 h-14 bg-error-container text-error rounded-xl flex items-center justify-center mb-6">
                  <span className="material-symbols-outlined text-3xl">
                    psychology_alt
                  </span>
                </div>
                <h3 className="text-xl font-bold mb-4">Incerteza Total</h3>
                <p className="text-muted">
                  Gastar dias gravando vídeos para produtos que ninguém quer
                  comprar ou que o algoritmo já ignorou.
                </p>
              </div>
              <div className="group bg-surface p-8 rounded-2xl shadow-sm hover:shadow-lg transition-all hover:-translate-y-2 border-transparent hover:border-outline-variant border-2">
                <div className="w-14 h-14 bg-error-container text-error rounded-xl flex items-center justify-center mb-6">
                  <span className="material-symbols-outlined text-3xl">
                    timer_off
                  </span>
                </div>
                <h3 className="text-xl font-bold mb-4">Saturação Relâmpago</h3>
                <p className="text-muted">
                  Chegar tarde demais em uma tendência e ver seu alcance
                  despencar enquanto o custo de estoque dos parceiros sobe.
                </p>
              </div>
              <div className="group bg-surface p-8 rounded-2xl shadow-sm hover:shadow-lg transition-all hover:-translate-y-2 border-transparent hover:border-outline-variant border-2">
                <div className="w-14 h-14 bg-error-container text-error rounded-xl flex items-center justify-center mb-6">
                  <span className="material-symbols-outlined text-3xl">
                    block
                  </span>
                </div>
                <h3 className="text-xl font-bold mb-4">Bloqueio Criativo</h3>
                <p className="text-muted">
                  Saber que o produto é bom, mas não ter ideia de qual gancho
                  usar para prender a atenção nos primeiros 3 segundos.
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* Solution Section - The Elite Toolkit */}
        <section id="raiox" className="py-24 px-6 overflow-hidden">
          <div className="max-w-7xl mx-auto">
            <div className="text-center mb-20">
              <h2 className="text-4xl md:text-5xl font-black tracking-tighter mb-4">
                Elite Toolkit
              </h2>
              <p className="text-muted max-w-2xl mx-auto">
                Deixe de ser um criador de conteúdo e torne-se uma máquina de
                vendas orientada a dados.
              </p>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-12 gap-6 md:h-[600px]">
              {/* Radar Semanal */}
              <div className="md:col-span-7 bg-surface border-2 border-outline-variant rounded-2xl p-8 relative overflow-hidden group">
                <div className="relative z-10 h-full flex flex-col justify-between">
                  <div>
                    <span className="bg-accent/10 text-accent px-3 py-1 rounded-md text-xs font-black uppercase tracking-widest mb-4 inline-block">
                      Módulo 01
                    </span>
                    <h3 className="text-3xl font-black mb-4">Radar Semanal</h3>
                    <p className="text-muted max-w-sm mb-6">
                      Curadoria feita por humanos e IA dos 10 produtos com maior
                      potencial de explosão na semana.
                    </p>
                    <ul className="space-y-3">
                      <li className="flex items-center gap-2 font-bold text-sm">
                        <span
                          className="material-symbols-outlined text-success"
                          style={{ fontVariationSettings: "'FILL' 1" }}
                        >
                          check_circle
                        </span>
                        Análise de Volume de Busca
                      </li>
                      <li className="flex items-center gap-2 font-bold text-sm">
                        <span
                          className="material-symbols-outlined text-success"
                          style={{ fontVariationSettings: "'FILL' 1" }}
                        >
                          check_circle
                        </span>
                        Pontuação de Saturação
                      </li>
                    </ul>
                  </div>
                  <div className="mt-8">
                    <img
                      className="w-full h-48 object-cover rounded-xl shadow-inner grayscale group-hover:grayscale-0 transition-all duration-500"
                      alt="Abstract visualization of data trends and social media metrics"
                      src="https://lh3.googleusercontent.com/aida-public/AB6AXuCXmEw_Qm2kLA9pzH-K_WulrhjaLRwVJHYOice0iIF0SW-yfSfCL8xo7HqCwRyWcdsPydioP1n9Rb474yw2iIe0p8HGmkrr23e00BaxaVuWZWLJq0nO8V0r9yRkES2JYQ2ZNC8XOyPPGRR8H8vCXlOvwCgG4jiSE6UZAoAG1loyZEXwtae5h_1Ok6hVDMHjcDI766wFjYnyNmLuYD2_aC-0uit6mmLnQ24mG59Yd8EjwxBpO8F507grmdnt-kgLeWjCoGvN9A4GddT-"
                    />
                  </div>
                </div>
              </div>
              {/* Raio-X do Produto */}
              <div className="md:col-span-5 bg-primary text-white rounded-2xl p-8 flex flex-col justify-between relative overflow-hidden group">
                <div className="absolute top-0 right-0 w-32 h-32 bg-white/10 rounded-full blur-3xl -mr-16 -mt-16 group-hover:scale-150 transition-transform duration-700"></div>
                <div className="relative z-10">
                  <span className="bg-white/20 text-white px-3 py-1 rounded-md text-xs font-black uppercase tracking-widest mb-4 inline-block">
                    Módulo 02
                  </span>
                  <h3 className="text-3xl font-black mb-4">
                    Raio-X do Produto
                  </h3>
                  <p className="text-primary-container leading-relaxed">
                    Vá além do preço. Saiba exatamente qual a margem real, tempo
                    de entrega e reputação do fornecedor.
                  </p>
                </div>
                <div className="mt-8 bg-white/10 backdrop-blur-md rounded-xl p-4 border border-white/20">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs font-bold opacity-70">
                      Supply Health
                    </span>
                    <span className="text-xs font-bold">98/100</span>
                  </div>
                  <div className="w-full bg-white/20 h-2 rounded-full overflow-hidden">
                    <div className="bg-success w-[98%] h-full"></div>
                  </div>
                </div>
              </div>
              {/* Laboratório de Ângulos */}
              <div
                id="lab"
                className="md:col-span-12 bg-background-light dark:bg-background-dark border-2 border-outline-variant rounded-2xl p-8 flex flex-col md:flex-row items-center gap-12 group"
              >
                <div className="flex-1 order-2 md:order-1">
                  <span className="bg-success/10 text-success px-3 py-1 rounded-md text-xs font-black uppercase tracking-widest mb-4 inline-block">
                    Módulo 03
                  </span>
                  <h3 className="text-3xl font-black mb-4">
                    Laboratório de Ângulos
                  </h3>
                  <p className="text-muted text-lg mb-8">
                    Não apenas o que vender, mas COMO vender. Receba roteiros
                    prontos e ganchos validados para cada produto do Radar.
                  </p>
                  <div className="flex flex-wrap gap-3">
                    <span className="px-4 py-2 bg-white rounded-full text-xs font-bold shadow-sm border border-outline">
                      Gancho: Problem-First
                    </span>
                    <span className="px-4 py-2 bg-white rounded-full text-xs font-bold shadow-sm border border-outline">
                      Ângulo: Review Honesto
                    </span>
                    <span className="px-4 py-2 bg-white rounded-full text-xs font-bold shadow-sm border border-outline">
                      Gancho: ASMR Unboxing
                    </span>
                  </div>
                </div>
                <div className="flex-1 order-1 md:order-2 w-full">
                  <div className="aspect-video bg-zinc-900 rounded-2xl relative overflow-hidden flex items-center justify-center">
                    <img
                      className="absolute inset-0 w-full h-full object-cover opacity-50"
                      alt="Creative process workspace with lights and microphone"
                      src="https://lh3.googleusercontent.com/aida-public/AB6AXuAkUBQgi0gZGuJfnpaQR_FhCIx6tVOgEWtv7a4qfFcfj9MSpQayU9Za2Usxq-ZRs3PX9h7qevftJF3Fzzh0Ib3gzA_GoM-OFYsEkQoe0WbSMtG0-X2h5KbH0xky9sV7pjDi-1aM_pXp_OmGj612d_Cs9RjnA7Cmm0H8Nifh3xtMkQMiQaHRqb1oVmhCpX2D1kZMdM85F7tO2nKD2VLQxm55_xlqvEH6dtMc3HGHzQio4ZJFDL9Z0n3VpLlQBG4GESx1ZnaY2TRICoFV"
                    />
                    <div className="relative z-10 w-16 h-16 bg-primary rounded-full flex items-center justify-center text-white cursor-pointer hover:scale-110 transition-transform">
                      <span
                        className="material-symbols-outlined text-4xl"
                        style={{ fontVariationSettings: "'FILL' 1" }}
                      >
                        play_arrow
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Pricing Section */}
        <section
          id="precos"
          className="py-24 px-6 bg-background-light dark:bg-background-dark"
        >
          <div className="max-w-7xl mx-auto">
            <div className="text-center mb-16">
              <h2 className="text-4xl md:text-5xl font-black tracking-tighter mb-4">
                Escolha seu Nível de Jogo
              </h2>
              <p className="text-muted">
                Planos que acompanham sua jornada de criador.
              </p>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8 items-end">
              {/* Básico */}
              <div className="bg-surface p-8 rounded-2xl shadow-sm border border-outline space-y-8">
                <div>
                  <h3 className="text-xl font-bold mb-2">Plano Básico</h3>
                  <div className="flex items-baseline gap-1">
                    <span className="text-4xl font-black text-text-main dark:text-white">
                      R$49
                    </span>
                    <span className="text-muted font-medium">/mês</span>
                  </div>
                </div>
                <ul className="space-y-4 border-t border-outline pt-8">
                  <li className="flex items-center gap-3 text-sm text-muted">
                    <span className="material-symbols-outlined text-primary text-lg">
                      check
                    </span>
                    Radar Semanal (Top 5)
                  </li>
                  <li className="flex items-center gap-3 text-sm text-muted">
                    <span className="material-symbols-outlined text-primary text-lg">
                      check
                    </span>
                    Suporte via Email
                  </li>
                  <li className="flex items-center gap-3 text-sm text-muted">
                    <span className="material-symbols-outlined text-primary text-lg">
                      check
                    </span>
                    Acesso ao Dashboard
                  </li>
                </ul>
                <button
                  onClick={() => navigate("/login")}
                  className="w-full py-4 rounded-xl border-2 border-primary text-primary font-bold hover:bg-primary/5 transition-colors"
                >
                  Assinar Agora
                </button>
              </div>
              {/* Criador Pro */}
              <div className="bg-surface p-8 rounded-2xl shadow-2xl border-4 border-primary space-y-8 relative transform md:scale-105 z-10">
                <div className="absolute -top-5 left-1/2 -translate-x-1/2 bg-primary text-white px-4 py-1 rounded-full text-xs font-black uppercase tracking-widest">
                  Mais Popular
                </div>
                <div>
                  <h3 className="text-xl font-bold mb-2">Plano Criador Pro</h3>
                  <div className="flex items-baseline gap-1">
                    <span className="text-5xl font-black text-text-main dark:text-white">
                      R$99
                    </span>
                    <span className="text-muted font-medium">/mês</span>
                  </div>
                </div>
                <ul className="space-y-4 border-t border-outline pt-8">
                  <li className="flex items-center gap-3 text-sm font-bold">
                    <span
                      className="material-symbols-outlined text-primary text-lg"
                      style={{ fontVariationSettings: "'FILL' 1" }}
                    >
                      check_circle
                    </span>
                    Radar Semanal Completo (Top 10)
                  </li>
                  <li className="flex items-center gap-3 text-sm font-bold">
                    <span
                      className="material-symbols-outlined text-primary text-lg"
                      style={{ fontVariationSettings: "'FILL' 1" }}
                    >
                      check_circle
                    </span>
                    Laboratório de Ângulos (Scripts)
                  </li>
                  <li className="flex items-center gap-3 text-sm font-bold">
                    <span
                      className="material-symbols-outlined text-primary text-lg"
                      style={{ fontVariationSettings: "'FILL' 1" }}
                    >
                      check_circle
                    </span>
                    Raio-X do Fornecedor
                  </li>
                  <li className="flex items-center gap-3 text-sm font-bold">
                    <span
                      className="material-symbols-outlined text-primary text-lg"
                      style={{ fontVariationSettings: "'FILL' 1" }}
                    >
                      check_circle
                    </span>
                    Comunidade Exclusiva Discord
                  </li>
                </ul>
                <button
                  onClick={() => navigate("/login")}
                  className="w-full py-4 rounded-xl bg-primary text-white font-black text-lg hover:shadow-xl hover:scale-[1.02] transition-all shadow-md"
                >
                  Começar Agora
                </button>
              </div>
              {/* Agência */}
              <div className="bg-surface p-8 rounded-2xl shadow-sm border border-outline space-y-8">
                <div>
                  <h3 className="text-xl font-bold mb-2">Plano Agência</h3>
                  <div className="flex items-baseline gap-1">
                    <span className="text-4xl font-black text-text-main dark:text-white">
                      R$249
                    </span>
                    <span className="text-muted font-medium">/mês</span>
                  </div>
                </div>
                <ul className="space-y-4 border-t border-outline pt-8">
                  <li className="flex items-center gap-3 text-sm text-muted">
                    <span className="material-symbols-outlined text-primary text-lg">
                      check
                    </span>
                    Até 5 Contas de Criador
                  </li>
                  <li className="flex items-center gap-3 text-sm text-muted">
                    <span className="material-symbols-outlined text-primary text-lg">
                      check
                    </span>
                    Relatórios Customizados
                  </li>
                  <li className="flex items-center gap-3 text-sm text-muted">
                    <span className="material-symbols-outlined text-primary text-lg">
                      check
                    </span>
                    API de Dados TikTrends
                  </li>
                  <li className="flex items-center gap-3 text-sm text-muted">
                    <span className="material-symbols-outlined text-primary text-lg">
                      check
                    </span>
                    Gerente de Conta Dedicado
                  </li>
                </ul>
                <button
                  onClick={() => navigate("/login")}
                  className="w-full py-4 rounded-xl border-2 border-primary text-primary font-bold hover:bg-primary/5 transition-colors"
                >
                  Falar com Consultor
                </button>
              </div>
            </div>
          </div>
        </section>

        {/* Final CTA */}
        <section className="py-24 px-6 relative overflow-hidden">
          <div className="absolute inset-0 bg-primary/5"></div>
          <div className="max-w-4xl mx-auto text-center relative z-10">
            <h2 className="text-4xl md:text-6xl font-black tracking-tighter mb-8 leading-tight">
              Chega de tentar adivinhar o que vai vender.
            </h2>
            <p className="text-xl text-muted mb-12">
              Junte-se a mais de 2.500 afiliados que utilizam o Radar para
              escalar suas operações no TikTok Shop.
            </p>
            <div className="flex flex-col sm:flex-row gap-6 justify-center items-center">
              <button
                onClick={() => navigate("/login")}
                className="bg-primary text-white px-12 py-5 rounded-2xl font-black text-xl hover:scale-105 transition-all shadow-2xl"
              >
                Assinar Radar Agora
              </button>
              <p className="text-sm font-bold text-muted flex items-center gap-2">
                <span className="material-symbols-outlined text-success">
                  verified_user
                </span>
                Cancelamento a qualquer momento
              </p>
            </div>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="w-full py-12 bg-background-light dark:bg-background-dark border-t-2 border-outline dark:border-outline/20">
        <div className="flex flex-col md:flex-row justify-between items-center max-w-7xl mx-auto px-6 gap-8">
          <div className="flex flex-col gap-4 items-center md:items-start">
            <div className="text-xl font-black text-text-main dark:text-white dark:text-white">
              Radar
            </div>
            <p className="font-['Inter'] text-sm text-muted">
              © 2024 Radar. O pulso do TikTok Shop.
            </p>
          </div>
          <div className="flex gap-8">
            <a
              className="text-muted hover:text-primary transition-colors text-sm hover:underline"
              href="#"
            >
              Termos
            </a>
            <a
              className="text-muted hover:text-primary transition-colors text-sm hover:underline"
              href="#"
            >
              Privacidade
            </a>
            <a
              className="text-muted hover:text-primary transition-colors text-sm hover:underline"
              href="#"
            >
              Suporte
            </a>
            <a
              className="text-muted hover:text-primary transition-colors text-sm hover:underline"
              href="#"
            >
              Afiliados
            </a>
          </div>
          <div className="flex gap-4">
            <div className="w-10 h-10 rounded-full bg-outline dark:bg-surface-dark flex items-center justify-center text-muted cursor-pointer hover:bg-primary hover:text-white transition-all">
              <span className="material-symbols-outlined">share</span>
            </div>
            <div className="w-10 h-10 rounded-full bg-outline dark:bg-surface-dark flex items-center justify-center text-muted cursor-pointer hover:bg-primary hover:text-white transition-all">
              <span className="material-symbols-outlined">forum</span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}

import React, { useState } from "react";
import { useNavigate } from "react-router-dom";

export function LoginPage() {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const handleLogin = (e) => {
    e.preventDefault();
    if (email && password) {
      navigate("/");
    }
  };

  return (
    <div className="min-h-screen flex text-on-surface font-body">
      {/* Left Area - Creative Content */}
      <div className="hidden lg:flex w-[55%] relative bg-background-dark p-12 xl:p-20 flex-col justify-between overflow-hidden">
        {/* Abstract/Tech Background Image Placeholder */}
        <div className="absolute inset-0 z-0 bg-background-dark">
          <img
            src="/login-bg-3.jpg"
            alt="Workspace"
            className="w-full h-full object-cover opacity-80 contrast-125 saturate-110 brightness-105 transition-all"
          />
          <div className="absolute inset-0 bg-gradient-to-t from-zinc-950 via-zinc-950/40 to-transparent"></div>
          <div className="absolute inset-0 bg-gradient-to-r from-zinc-950/90 via-zinc-950/10 to-transparent"></div>
        </div>

        <div className="relative z-10 flex flex-col pt-10 mt-8">
          <h1 className="text-5xl xl:text-7xl font-black tracking-tighter text-white leading-[1.05] mb-6">
            Transforme sua
            <br />
            <span className="text-primary">criatividade</span> em
            <br />
            impacto.
          </h1>
          <p className="text-muted text-lg xl:text-xl max-w-[400px] leading-relaxed mb-10 font-medium">
            Acesse a inteligencia semanal do TikTok Shop. Descubra produtos
            antes que eles saturem.
          </p>

          <div className="flex gap-4">
            <div className="glass-card bg-white/5 border border-white/10 p-5 rounded-2xl w-44 backdrop-blur-xl">
              <div className="text-4xl font-black text-primary mb-2">98%</div>
              <div className="text-[11px] font-bold text-white tracking-widest uppercase opacity-80">
                PRECISÃO DE DADOS
              </div>
            </div>
            <div className="glass-card bg-white/5 border border-white/10 p-5 rounded-2xl w-44 backdrop-blur-xl">
              <div className="text-4xl font-black text-primary mb-2">+15k</div>
              <div className="text-[11px] font-bold text-white tracking-widest uppercase opacity-80">
                CREATORS ATIVOS
              </div>
            </div>
          </div>
        </div>

        <div className="relative z-10 flex items-center gap-2 mb-4">
          <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center text-white">
            <span className="material-symbols-outlined text-sm">radar</span>
          </div>
          <span
            className="text-2xl font-black text-white tracking-tighter cursor-pointer"
            onClick={() => navigate("/landing")}
          >
            Radar
          </span>
        </div>
      </div>

      {/* Right Area - Form */}
      <div className="w-full lg:w-[45%] flex flex-col justify-center items-center bg-white p-6 relative">
        <div className="w-full max-w-sm">
          <h2 className="text-[32px] font-black text-center mb-10 text-text-main">
            Bem-vindo de volta
          </h2>

          <div className="space-y-4 mb-8">
            <button className="w-full flex items-center justify-center gap-3 bg-text-main text-white font-bold py-[14px] rounded-lg hover:bg-zinc-800 transition-colors shadow-sm">
              <img
                src="https://www.svgrepo.com/show/365518/tiktok.svg"
                alt="TikTok"
                className="w-[18px] h-[18px] filter invert"
              />
              Entrar com TikTok
            </button>
            <button className="w-full flex items-center justify-center gap-3 bg-white border border-outline text-text-main font-bold py-[14px] rounded-lg hover:bg-zinc-50 transition-colors shadow-sm">
              <img
                src="https://www.svgrepo.com/show/475656/google-color.svg"
                alt="Google"
                className="w-[18px] h-[18px]"
              />
              Entrar com Google
            </button>
          </div>

          <div className="relative flex items-center mb-8">
            <div className="flex-grow border-t border-outline"></div>
            <span className="flex-shrink-0 mx-4 text-muted text-[11px] font-bold uppercase tracking-wider">
              OU USE SEU E-MAIL
            </span>
            <div className="flex-grow border-t border-outline"></div>
          </div>

          <form onSubmit={handleLogin} className="space-y-6">
            <div>
              <label
                className="block text-[11px] font-bold text-text-main mb-2 uppercase tracking-wide"
                htmlFor="email"
              >
                E-MAIL
              </label>
              <input
                id="email"
                type="email"
                className="w-full border border-outline text-text-main rounded-lg p-3.5 focus:ring-2 focus:ring-primary focus:border-transparent transition-all outline-none font-medium placeholder-muted"
                placeholder="E-mail@e-mail.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </div>

            <div>
              <label
                className="block text-[11px] font-bold text-text-main mb-2 uppercase tracking-wide"
                htmlFor="password"
              >
                SENHA
              </label>
              <input
                id="password"
                type="password"
                className="w-full border border-outline text-text-main rounded-lg p-3.5 focus:ring-2 focus:ring-primary focus:border-transparent transition-all outline-none font-medium mb-2 placeholder-muted"
                placeholder="Senha"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
              <div className="flex justify-end">
                <a
                  href="#"
                  className="text-xs font-medium text-text-main hover:text-primary transition-colors"
                >
                  Esqueceu a senha?
                </a>
              </div>
            </div>

            <button
              type="submit"
              className="w-full bg-primary text-white font-black py-4 rounded-lg hover:bg-primary/90 transition-all shadow-md mt-4 uppercase text-sm tracking-wide"
            >
              ENTRAR
            </button>
          </form>

          <p className="text-center text-sm font-medium text-text-main mt-8">
            Ainda não tem conta?{" "}
            <a
              href="#"
              onClick={(e) => {
                e.preventDefault();
                navigate("/landing");
              }}
              className="font-black hover:underline"
            >
              Cadastre-se
            </a>
          </p>
        </div>

        <div className="absolute bottom-10 flex gap-8 text-[13px] text-muted font-medium">
          <a href="#" className="hover:text-text-main transition-colors">
            Termos
          </a>
          <a href="#" className="hover:text-text-main transition-colors">
            Privacidade
          </a>
          <a href="#" className="hover:text-text-main transition-colors">
            Suporte
          </a>
        </div>
      </div>
    </div>
  );
}

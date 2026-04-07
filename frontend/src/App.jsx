import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { AppShell } from "./components/layout/AppShell";
import { RankingDashboard } from "./components/dashboard/RankingDashboard";
import { ProductDetail } from "./pages/ProductDetail";
import { ContentIdeas } from "./pages/ContentIdeas";
import { SavedProducts } from "./pages/SavedProducts";
import { PipelineHistory } from "./pages/PipelineHistory";
import { LandingPage } from "./pages/LandingPage";
import { LoginPage } from "./pages/LoginPage";

function App() {
  return (
    <Router>
      <Routes>
        {/* Rotas Públicas */}
        <Route path="/landing" element={<LandingPage />} />
        <Route path="/login" element={<LoginPage />} />

        {/* Rotas da Aplicação que requerem o AppShell */}
        <Route
          path="/*"
          element={
            <AppShell>
              <Routes>
                <Route path="/" element={<RankingDashboard />} />
                <Route path="/product/:id" element={<ProductDetail />} />
                <Route path="/ideas" element={<ContentIdeas />} />
                <Route path="/history" element={<PipelineHistory />} />
                <Route path="/garage" element={<SavedProducts />} />
              </Routes>
            </AppShell>
          }
        />
      </Routes>
    </Router>
  );
}

export default App;

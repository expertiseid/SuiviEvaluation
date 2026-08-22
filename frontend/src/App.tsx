import { Route, Routes } from "react-router-dom";
import { AppLayout } from "./layouts/AppLayout";
import { RequireAuth } from "./auth/RequireAuth";
import { LoginPage } from "./auth/LoginPage";
import { DashboardConsolidePage } from "./pages/DashboardConsolidePage";
import { ProjetsListPage } from "./pages/projets/ProjetsListPage";
import { ProjetDetailPage } from "./pages/projets/ProjetDetailPage";
import { IndicateursListPage } from "./pages/indicateurs/IndicateursListPage";
import { IndicateurDetailPage } from "./pages/indicateurs/IndicateurDetailPage";
import { SuiviPage } from "./pages/suivi/SuiviPage";
import { SuiviProjetDashboard } from "./pages/suivi/SuiviProjetDashboard";
import { BeneficiairesListPage } from "./pages/beneficiaires/BeneficiairesListPage";
import { DoublonsPage } from "./pages/beneficiaires/DoublonsPage";
import { RapportsListPage } from "./pages/rapports/RapportsListPage";
import { UtilisateursPage } from "./pages/utilisateurs/UtilisateursPage";
import { CadresStrategiquesListPage } from "./pages/strategie/CadresStrategiquesListPage";
import { CadreStrategiqueDetailPage } from "./pages/strategie/CadreStrategiqueDetailPage";
import { ZonesAdministrativesPage } from "./pages/geo/ZonesAdministrativesPage";
import { PlanificationImportPage } from "./pages/planification/PlanificationImportPage";
import { ParametresAlertePage } from "./pages/parametres/ParametresAlertePage";

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route
        element={
          <RequireAuth>
            <AppLayout />
          </RequireAuth>
        }
      >
        <Route path="/" element={<DashboardConsolidePage />} />
        <Route path="/projets" element={<ProjetsListPage />} />
        <Route path="/projets/:id" element={<ProjetDetailPage />} />
        <Route path="/indicateurs" element={<IndicateursListPage />} />
        <Route path="/indicateurs/:id" element={<IndicateurDetailPage />} />
        <Route path="/suivi" element={<SuiviPage />} />
        <Route path="/suivi/:id" element={<SuiviProjetDashboard />} />
        <Route path="/beneficiaires" element={<BeneficiairesListPage />} />
        <Route path="/doublons" element={<DoublonsPage />} />
        <Route path="/rapports" element={<RapportsListPage />} />
        <Route path="/strategie" element={<CadresStrategiquesListPage />} />
        <Route path="/strategie/:id" element={<CadreStrategiqueDetailPage />} />
        <Route path="/zones-administratives" element={<ZonesAdministrativesPage />} />
        <Route path="/planification" element={<PlanificationImportPage />} />
        <Route
          path="/utilisateurs"
          element={
            <RequireAuth roles={["ADMIN"]}>
              <UtilisateursPage />
            </RequireAuth>
          }
        />
        <Route
          path="/parametres-alerte"
          element={
            <RequireAuth roles={["ADMIN"]}>
              <ParametresAlertePage />
            </RequireAuth>
          }
        />
      </Route>
    </Routes>
  );
}

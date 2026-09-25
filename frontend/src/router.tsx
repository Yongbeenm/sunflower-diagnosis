import React, { Suspense, lazy } from "react";
import { createBrowserRouter, Outlet } from "react-router";
import { AppLayout } from "./components/layout/AppLayout";
import { Skeleton } from "./components/ui/Skeleton";

// Public / Grower pages
const LandingPage = lazy(() =>
  import("./features/landing/LandingPage").then((m) => ({ default: m.LandingPage })),
);
const DiseasesPage = lazy(() =>
  import("./features/diseases/pages/DiseasesPage").then((m) => ({ default: m.DiseasesPage })),
);
const DiseaseComparePage = lazy(() =>
  import("./features/diseases/pages/DiseaseComparePage").then((m) => ({
    default: m.DiseaseComparePage,
  })),
);
const DiseaseDetailPage = lazy(() =>
  import("./features/diseases/pages/DiseaseDetailPage").then((m) => ({
    default: m.DiseaseDetailPage,
  })),
);
const CheckerPage = lazy(() =>
  import("./features/diagnosis/pages/CheckerPage").then((m) => ({ default: m.CheckerPage })),
);
const ResultPage = lazy(() =>
  import("./features/diagnosis/pages/ResultPage").then((m) => ({ default: m.ResultPage })),
);
const HistoryPage = lazy(() =>
  import("./features/history/pages/HistoryPage").then((m) => ({ default: m.HistoryPage })),
);
const FeedbackPage = lazy(() =>
  import("./features/feedback/pages/FeedbackPage").then((m) => ({ default: m.FeedbackPage })),
);
const LoginPage = lazy(() =>
  import("./features/auth/pages/LoginPage").then((m) => ({ default: m.LoginPage })),
);
const RegisterPage = lazy(() =>
  import("./features/auth/pages/RegisterPage").then((m) => ({ default: m.RegisterPage })),
);
const ProfilePage = lazy(() =>
  import("./features/auth/pages/ProfilePage").then((m) => ({ default: m.ProfilePage })),
);

// Admin & Agronomist pages
const AdminLayout = lazy(() =>
  import("./features/admin/components/AdminLayout").then((m) => ({ default: m.AdminLayout })),
);
const AdminOverviewPage = lazy(() =>
  import("./features/admin/pages/OverviewPage").then((m) => ({ default: m.OverviewPage })),
);
const AdminDiseasesPage = lazy(() =>
  import("./features/admin/pages/DiseasesPage").then((m) => ({ default: m.DiseasesPage })),
);
const AdminDiseaseCreatePage = lazy(() =>
  import("./features/admin/pages/DiseaseCreatePage").then((m) => ({
    default: m.DiseaseCreatePage,
  })),
);
const AdminDiseaseEditorPage = lazy(() =>
  import("./features/admin/pages/DiseaseEditorPage").then((m) => ({
    default: m.DiseaseEditorPage,
  })),
);
const AdminSymptomsPage = lazy(() =>
  import("./features/admin/pages/SymptomsPage").then((m) => ({ default: m.SymptomsPage })),
);
const AdminFeedbackPage = lazy(() =>
  import("./features/admin/pages/FeedbackPage").then((m) => ({ default: m.FeedbackPage })),
);
const AdminUsersPage = lazy(() =>
  import("./features/admin/pages/UsersPage").then((m) => ({ default: m.UsersPage })),
);
const AdminRolesPage = lazy(() =>
  import("./features/admin/pages/RolesPage").then((m) => ({ default: m.RolesPage })),
);
const AdminRulesetsPage = lazy(() =>
  import("./features/admin/pages/RulesetsPage").then((m) => ({ default: m.RulesetsPage })),
);

function RootLayout(): React.JSX.Element {
  return (
    <AppLayout>
      <Suspense
        fallback={
          <div style={{ padding: "2rem 0" }} aria-busy="true">
            <Skeleton height="2.5rem" width="35%" className="mb-4" />
            <Skeleton height="1.25rem" width="60%" className="mb-6" />
            <Skeleton height="15rem" className="rounded-xl" />
          </div>
        }
      >
        <Outlet />
      </Suspense>
    </AppLayout>
  );
}

function AdminRootLayout(): React.JSX.Element {
  return (
    <Suspense
      fallback={
        <div style={{ minHeight: "100vh", display: "grid", placeItems: "center" }}>
          <div className="sf-spinner" aria-label="Loading admin portal..." />
        </div>
      }
    >
      <AdminLayout />
    </Suspense>
  );
}

export const router = createBrowserRouter([
  {
    element: <RootLayout />,
    children: [
      {
        path: "/",
        element: <LandingPage />,
      },
      {
        path: "/diseases",
        element: <DiseasesPage />,
      },
      {
        path: "/diseases/compare",
        element: <DiseaseComparePage />,
      },
      {
        path: "/diseases/:slug",
        element: <DiseaseDetailPage />,
      },
      {
        path: "/check",
        element: <CheckerPage />,
      },
      {
        path: "/check/:sessionId",
        element: <ResultPage />,
      },
      {
        path: "/history",
        element: <HistoryPage />,
      },
      {
        path: "/feedback",
        element: <FeedbackPage />,
      },
      {
        path: "/profile",
        element: <ProfilePage />,
      },
      {
        path: "/login",
        element: <LoginPage />,
      },
      {
        path: "/register",
        element: <RegisterPage />,
      },
    ],
  },
  {
    path: "/admin",
    element: <AdminRootLayout />,
    children: [
      {
        index: true,
        element: <AdminOverviewPage />,
      },
      {
        path: "diseases",
        element: <AdminDiseasesPage />,
      },
      {
        path: "diseases/new",
        element: <AdminDiseaseCreatePage />,
      },
      {
        path: "diseases/:id",
        element: <AdminDiseaseEditorPage />,
      },
      {
        path: "symptoms",
        element: <AdminSymptomsPage />,
      },
      {
        path: "feedback",
        element: <AdminFeedbackPage />,
      },
      {
        path: "users",
        element: <AdminUsersPage />,
      },
      {
        path: "roles",
        element: <AdminRolesPage />,
      },
      {
        path: "rulesets",
        element: <AdminRulesetsPage />,
      },
    ],
  },
]);

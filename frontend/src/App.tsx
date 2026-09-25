import { RouterProvider } from "react-router";
import { AuthProvider } from "./features/auth";
import { router } from "./router";

export default function App() {
  return (
    <AuthProvider onSessionExpired={() => void router.navigate("/login")}>
      <RouterProvider router={router} />
    </AuthProvider>
  );
}

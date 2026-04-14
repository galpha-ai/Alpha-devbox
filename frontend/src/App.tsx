import { Suspense, lazy } from "react";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import NotFound from "./pages/NotFound.tsx";

const WebChatPage = lazy(() => import("./pages/WebChatPage.tsx"));
const App = () => (
  <BrowserRouter>
    <Suspense fallback={<div className="flex min-h-screen items-center justify-center bg-background text-sm text-muted-foreground">Loading workspace...</div>}>
      <Routes>
        <Route path="/" element={<WebChatPage />} />
        <Route path="*" element={<NotFound />} />
      </Routes>
    </Suspense>
  </BrowserRouter>
);

export default App;

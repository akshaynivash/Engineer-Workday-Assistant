import { BrowserRouter, Routes, Route } from "react-router-dom";

import { Layout } from "@/components/Layout";
import Home from "@/pages/Home";
import PartSourcing from "@/pages/PartSourcing";
import QuickChat from "@/pages/QuickChat";
import WorkdayHelp from "@/pages/WorkdayHelp";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route path="/" element={<Home />} />
          <Route path="/parts" element={<PartSourcing />} />
          <Route path="/chat" element={<QuickChat />} />
          <Route path="/assistant" element={<WorkdayHelp />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

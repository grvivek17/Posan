import { BrowserRouter, Routes, Route, NavLink } from "react-router-dom";
import {
  Upload,
  Sparkles,
  ClipboardList,
  Phone,
  LayoutDashboard,
} from "lucide-react";
import ResumeUpload from "./pages/ResumeUpload";
import TalentFinder from "./pages/TalentFinder";
import Requirements from "./pages/Requirements";
import Telecaller from "./pages/Telecaller";

const navItems = [
  { to: "/", icon: Upload, label: "Resume Upload" },
  { to: "/talent-finder", icon: Sparkles, label: "Talent Finder" },
  { to: "/requirements", icon: ClipboardList, label: "Requirements" },
  { to: "/telecaller", icon: Phone, label: "Telecaller" },
];

function Layout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex h-screen bg-background">
      {/* Sidebar */}
      <aside className="w-64 border-r bg-card flex flex-col shrink-0">
        <div className="p-6 border-b">
          <div className="flex items-center gap-2">
            <LayoutDashboard className="h-6 w-6 text-primary" />
            <h1 className="text-lg font-bold">Talent Manager</h1>
          </div>
          <p className="text-xs text-muted-foreground mt-1">AI-Powered Talent Platform</p>
        </div>
        <nav className="flex-1 p-3 space-y-1">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.to === "/"}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                  isActive
                    ? "bg-primary text-primary-foreground"
                    : "text-muted-foreground hover:bg-muted hover:text-foreground"
                }`
              }
            >
              <item.icon className="h-4 w-4" />
              {item.label}
            </NavLink>
          ))}
        </nav>
        <div className="p-4 border-t">
          <p className="text-xs text-muted-foreground text-center">Powered by Infosys AI Gateway</p>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-auto">
        <div className="p-8 max-w-6xl mx-auto h-full">{children}</div>
      </main>
    </div>
  );
}

function App() {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/" element={<ResumeUpload />} />
          <Route path="/talent-finder" element={<TalentFinder />} />
          <Route path="/requirements" element={<Requirements />} />
          <Route path="/telecaller" element={<Telecaller />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  );
}

export default App;

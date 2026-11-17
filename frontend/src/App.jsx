import { lazy, Suspense } from 'react';
import { Toaster } from "@/components/ui/toaster"
import { QueryClientProvider } from '@tanstack/react-query'
import { queryClientInstance } from '@/lib/query-client'
import { BrowserRouter as Router, Route, Routes, Navigate } from 'react-router-dom';
import PageNotFound from './lib/PageNotFound';
import { AuthProvider, useAuth } from '@/lib/AuthContext';
import UserNotRegisteredError from '@/components/UserNotRegisteredError';
import ScrollToTop from './components/ScrollToTop';
import ProtectedRoute from '@/components/ProtectedRoute';

import Login from '@/pages/Login';
const Register = lazy(() => import('@/pages/Register'));
const ForgotPassword = lazy(() => import('@/pages/ForgotPassword'));
const ResetPassword = lazy(() => import('@/pages/ResetPassword'));
import AppLayout from '@/components/layout/AppLayout';
const ScanIA = lazy(() => import('@/pages/ScanIA'));
const Calculateur = lazy(() => import('@/pages/Calculateur'));
const CarnetSante = lazy(() => import('@/pages/CarnetSante'));
const Meteo = lazy(() => import('@/pages/Meteo'));
const HubExperts = lazy(() => import('@/pages/HubExperts'));
const Conseils = lazy(() => import('@/pages/Conseils'));
const Communaute = lazy(() => import('@/pages/Communaute'));

const AuthenticatedApp = () => {
  const { isLoadingAuth, isLoadingPublicSettings, authError, navigateToLogin } = useAuth();

  if (isLoadingPublicSettings || isLoadingAuth) {
    return (
      <div className="fixed inset-0 flex items-center justify-center bg-[#EAF4EC]">
        <div className="flex flex-col items-center gap-3">
          <div className="w-10 h-10 border-4 border-[#12523A]/20 border-t-[#12523A] rounded-full animate-spin" />
          <p className="text-sm text-[#5B6B62] font-body">Chargement…</p>
        </div>
      </div>
    );
  }

  if (authError) {
    if (authError.type === 'user_not_registered') {
      return <UserNotRegisteredError />;
    } else if (authError.type === 'auth_required') {
      navigateToLogin();
      return null;
    }
  }

  return (
    <Suspense fallback={<div role="status" className="p-10 text-center text-sm text-[#64766a]">Chargement de votre espace…</div>}>
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route path="/forgot-password" element={<ForgotPassword />} />
      <Route path="/reset-password" element={<ResetPassword />} />
      <Route element={<ProtectedRoute unauthenticatedElement={<Navigate to="/login" replace />} />}>
        <Route element={<AppLayout />}>
          <Route path="/" element={<ScanIA />} />
          <Route path="/communaute" element={<Communaute />} />
          <Route path="/calculateur" element={<Calculateur />} />
          <Route path="/carnet" element={<CarnetSante />} />
          <Route path="/meteo" element={<Meteo />} />
          <Route path="/experts" element={<HubExperts />} />
          <Route path="/conseils" element={<Conseils />} />
        </Route>
      </Route>
      <Route path="*" element={<PageNotFound />} />
    </Routes>
    </Suspense>
  );
};

function App() {
  return (
    <AuthProvider>
      <QueryClientProvider client={queryClientInstance}>
        <Router>
          <ScrollToTop />
          <AuthenticatedApp />
        </Router>
        <Toaster />
      </QueryClientProvider>
    </AuthProvider>
  )
}

export default App
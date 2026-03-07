import { BrowserRouter } from 'react-router-dom';
import { useEffect } from 'react';
import useAuthStore from './store/authStore';
import AppRoutes from './routes';

function App() {
  const initialize = useAuthStore((state) => state.initialize);

  useEffect(() => {
    initialize();
  }, [initialize]);

  return (
    <BrowserRouter>
      <AppRoutes />
    </BrowserRouter>
  );
}

export default App;

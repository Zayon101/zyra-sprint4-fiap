import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import App from './App.tsx'
import './globals.css'

//Importando os objetos do react-router
import { createBrowserRouter, RouterProvider } from 'react-router';

// Importando os componentes de rota
import Home from './routes/Home';
import Sobre from './routes/Sobre';
import Missoes from './routes/Missoes';
import MissaoDetalhe from './routes/MissaoDetalhe';
import Integrantes from './routes/Integrantes';
import Faq from './routes/Faq';
import Contato from './routes/Contato';
import Error from './routes/Error';
import Painel from './routes/Painel';


// createBrowserRouter memoriza a lista de todos os caminhos disponíveis
const router = createBrowserRouter([
  {path: "/", element:<App/>, errorElement:<Error/>, children:[
    {path: "/", element:<Home/>},
    {path: "/sobre", element:<Sobre/>},
    {path: "/missoes", element:<Missoes/>},
    {path: "/missoes/:id", element:<MissaoDetalhe/>},
    {path: "/integrantes", element:<Integrantes/>},
    {path: "/faq", element:<Faq/>},
    {path: "/contato", element:<Contato/>},
    {path: "/painel", element:<Painel/>},
  ]}]);

// RouterProvider conecta a lista de rotas (router) ao restante da interface
createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <RouterProvider router={router} />
  </StrictMode>,
)
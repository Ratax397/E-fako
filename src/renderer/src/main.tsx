import './assets/main.css'
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import { Provider } from 'react-redux'
import { createBrowserRouter, RouterProvider } from 'react-router-dom'
import Store from './redux/Store'
import { PersistGate } from 'redux-persist/integration/react'
import { persistor } from './redux/Store'
import Login from './auth/login/Login'
import Register from './auth/register/Registe'
import Home from './pages/home/Home'
import Dashboard from './pages/dashboard/Dashboard'
import UtilisateurPage from './pages/utilisateurs/UtilisateurPage'

const route = createBrowserRouter([
  {
    path: '/',
    element: <App />,
    children: [
      {
        index: true,
        element: <Login />
      },

      {
        path: '/register',
        element: <Register />
      }
    ]
  },
  {
    path: '/home',
    element: <Home />,
    children: [
      {
        index: true,
        element: <Dashboard />
      },
      {
        path: '/home/utilisateur',
        element: <UtilisateurPage />
      }
    ]
  }
])
ReactDOM.createRoot(document.getElementById('root') as HTMLElement).render(
  <React.StrictMode>
    <Provider store={Store}>
      <PersistGate loading={null} persistor={persistor}>
        <RouterProvider router={route} />
      </PersistGate>
    </Provider>
  </React.StrictMode>
)

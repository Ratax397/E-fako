import { configureStore } from '@reduxjs/toolkit'
import { persistStore, persistReducer } from 'redux-persist'
import storage from 'redux-persist/lib/storage'
import activeLinkReducer from './slice/activeLinkSlice'
import userReducer from './slice/userSlice'


const activeLinkPersistConfig = {
  key: 'activeLink',
  storage,
  whitelist: ['activeName']
}

const userPersistConfig = {
  key: 'user',
  storage,
  whitelist: ['name']
}

const persistedActiveLinkReducer = persistReducer(activeLinkPersistConfig, activeLinkReducer)
const persistedUserReducer = persistReducer(userPersistConfig, userReducer)

const Store = configureStore({
  reducer: {
    activeLink: persistedActiveLinkReducer,
    user: persistedUserReducer
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: ['persist/PERSIST'] // amin redux vaovao ty efa tsy par defaut fa apaitaka karahan jo
      }
    })
})

export type RootState = ReturnType<typeof Store.getState>
export type AppDispatch = typeof Store.dispatch

export const persistor = persistStore(Store)
export default Store


package com.sultan.arabicai

import android.app.Application
import com.sultan.arabicai.data.seed.ContentSeeder
import com.sultan.arabicai.di.AppContainer
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.launch

class SultanApplication : Application() {

    lateinit var container: AppContainer
        private set

    private val applicationScope = CoroutineScope(SupervisorJob() + Dispatchers.IO)

    override fun onCreate() {
        super.onCreate()
        container = AppContainer(this)

        applicationScope.launch {
            ContentSeeder.seedAll(
                libraryRepository = container.libraryRepository,
                lessonRepository = container.lessonRepository,
                vocabularyRepository = container.vocabularyRepository,
                progressRepository = container.progressRepository
            )
        }
    }
}

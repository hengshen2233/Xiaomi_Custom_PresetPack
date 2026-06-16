package com.example.xiaomilut

import android.content.Context
import android.net.Uri
import android.os.Bundle
import android.widget.Toast
import androidx.activity.ComponentActivity
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import com.example.xiaomilut.ui.theme.XiaomiLutTheme
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import java.io.BufferedOutputStream
import java.io.IOException
import java.util.Locale
import java.util.zip.ZipEntry
import java.util.zip.ZipOutputStream

enum class ParamType {
    SELECT, INT, FLOAT1, FLOAT0
}

data class Parameter(
    val name: String,
    val file: String,
    val defaultValue: String,
    val type: ParamType,
    val options: List<String> = emptyList()
)

class MainActivity : ComponentActivity() {
    private val params = listOf(
        Parameter("自动曝光", "p_pref_camera_autoexposure", "1", ParamType.SELECT, listOf("0", "1")),
        Parameter("镜头", "p_pref_camera_manually_lens", "wide", ParamType.SELECT, listOf("wide", "tele")),
        Parameter("场景类型", "p_pref_camera_cv_type", "0", ParamType.SELECT, listOf("0", "1")),
        Parameter("格式", "p_pref_camera_raw", "JPEG", ParamType.SELECT, listOf("JPEG", "RAW")),
        Parameter("超清像素", "p_pref_ultra_pixel_167", "BYPASS", ParamType.SELECT, listOf("BYPASS", "OFF")),
        Parameter("白平衡", "p_pref_camera_whitebalance", "1", ParamType.INT),
        Parameter("变焦倍率", "p_pref_camera_zoom_retain", "1.0", ParamType.FLOAT1),
        Parameter("对焦位置", "p_pref_focus_position", "1000", ParamType.INT),
        Parameter("快门速度", "p_pref_qc_camera_exposuretime", "0", ParamType.INT),
        Parameter("感光度", "p_pref_qc_camera_iso", "0", ParamType.INT),
        Parameter("曝光补偿", "p_pref_qc_camera_pro_exposure_value", "0", ParamType.FLOAT0),
        Parameter("色温", "p_pref_qc_camera_style_color_temp", "0", ParamType.INT),
        Parameter("色调", "p_pref_qc_camera_style_color_tone", "0", ParamType.INT),
        Parameter("纹理", "p_pref_qc_camera_style_texture", "0", ParamType.INT),
        Parameter("影调", "p_pref_qc_camera_style_tone", "0", ParamType.INT),
        Parameter("饱和度", "p_pref_qc_camera_style_vibrance", "0", ParamType.INT)
    )

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContent {
            XiaomiLutTheme {
                MainScreen(params)
            }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun MainScreen(params: List<Parameter>) {
    val context = LocalContext.current
    val scope = rememberCoroutineScope()
    
    var presetName by remember { mutableStateOf("我的预设") }
    val paramValues = remember {
        mutableStateMapOf<String, String>().apply {
            params.forEach { put(it.name, it.defaultValue) }
        }
    }

    val createDocumentLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.CreateDocument("application/zip")
    ) { uri ->
        uri?.let {
            scope.launch {
                val success = generatePresetPack(context, it, params, paramValues)
                if (success) {
                    Toast.makeText(context, "预设包生成成功", Toast.LENGTH_SHORT).show()
                } else {
                    Toast.makeText(context, "生成失败，请检查资源文件", Toast.LENGTH_LONG).show()
                }
            }
        }
    }

    Scaffold(
        topBar = {
            TopAppBar(title = { Text("预设包制作工具") })
        },
        modifier = Modifier.fillMaxSize()
    ) { innerPadding ->
        Column(
            modifier = Modifier
                .padding(innerPadding)
                .padding(16.dp)
                .fillMaxSize()
        ) {
            OutlinedTextField(
                value = presetName,
                onValueChange = { presetName = it },
                label = { Text("预设包名称") },
                modifier = Modifier.fillMaxWidth()
            )
            
            Spacer(modifier = Modifier.height(16.dp))
            
            Text("参数设置", style = MaterialTheme.typography.titleMedium)
            LazyColumn(modifier = Modifier.weight(1f)) {
                items(params) { param ->
                    ParamRow(param, paramValues[param.name] ?: "") { newValue ->
                        paramValues[param.name] = newValue
                    }
                }
            }

            Button(
                onClick = {
                    createDocumentLauncher.launch("Manual_official_0_$presetName.zip")
                },
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(vertical = 8.dp)
            ) {
                Text("生成预设包")
            }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ParamRow(param: Parameter, value: String, onValueChange: (String) -> Unit) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 4.dp),
        verticalAlignment = Alignment.CenterVertically
    ) {
        Text(text = param.name, modifier = Modifier.width(100.dp))
        
        if (param.type == ParamType.SELECT) {
            var expanded by remember { mutableStateOf(false) }
            ExposedDropdownMenuBox(
                expanded = expanded,
                onExpandedChange = { expanded = !expanded },
                modifier = Modifier.weight(1f)
            ) {
                OutlinedTextField(
                    value = value,
                    onValueChange = {},
                    readOnly = true,
                    trailingIcon = { ExposedDropdownMenuDefaults.TrailingIcon(expanded = expanded) },
                    modifier = Modifier.menuAnchor(),
                    colors = ExposedDropdownMenuDefaults.outlinedTextFieldColors()
                )
                ExposedDropdownMenu(
                    expanded = expanded,
                    onDismissRequest = { expanded = false }
                ) {
                    param.options.forEach { option ->
                        DropdownMenuItem(
                            text = { Text(option) },
                            onClick = {
                                onValueChange(option)
                                expanded = false
                            }
                        )
                    }
                }
            }
        } else {
            OutlinedTextField(
                value = value,
                onValueChange = { onValueChange(it) },
                modifier = Modifier.weight(1f),
                singleLine = true
            )
        }
    }
}

suspend fun generatePresetPack(
    context: Context,
    uri: Uri,
    params: List<Parameter>,
    paramValues: Map<String, String>
): Boolean = withContext(Dispatchers.IO) {
    try {
        context.contentResolver.openOutputStream(uri)?.use { outputStream ->
            ZipOutputStream(BufferedOutputStream(outputStream)).use { zipOut ->
                // Add parameters
                params.forEach { param ->
                    val value = paramValues[param.name] ?: param.defaultValue
                    val formattedValue = formatValue(value, param.type)
                    
                    val dstName = when (param.name) {
                        "镜头", "超清像素" -> "${param.file}_$formattedValue"
                        "白平衡" -> "${param.file}_key_new_$formattedValue"
                        else -> "${param.file}_key_$formattedValue"
                    }
                    
                    addFileToZip(context, "Default/${param.file}", dstName, zipOut)
                }
                
                // Add static files
                listOf("ac", "t", "v_3").forEach { staticFile ->
                    addFileToZip(context, "Default/$staticFile", staticFile, zipOut)
                }
            }
        }
        true
    } catch (e: Exception) {
        e.printStackTrace()
        false
    }
}

private fun formatValue(value: String, type: ParamType): String {
    return try {
        when (type) {
            ParamType.FLOAT1 -> {
                val num = value.toFloat()
                String.format(Locale.US, "%.1f", num)
            }
            ParamType.FLOAT0 -> {
                val num = value.toFloat()
                if (num == num.toInt().toFloat()) {
                    num.toInt().toString()
                } else {
                    String.format(Locale.US, "%.1f", num)
                }
            }
            else -> value
        }
    } catch (e: Exception) {
        value
    }
}

private fun addFileToZip(
    context: Context,
    assetPath: String,
    zipPath: String,
    zipOut: ZipOutputStream
) {
    try {
        context.assets.open(assetPath).use { input ->
            val entry = ZipEntry(zipPath)
            zipOut.putNextEntry(entry)
            input.copyTo(zipOut)
            zipOut.closeEntry()
        }
    } catch (e: IOException) {
        // Log error or handle missing assets
    }
}

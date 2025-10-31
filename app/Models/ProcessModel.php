<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class ProcessModel extends Model
{
    use HasFactory;

    protected $table = 'processes';

    protected $fillable = [
        'license_id',
        'protocol_number',
        'current_status',
        'timeline',
    ];

    protected $casts = [
        'timeline' => 'array',
    ];

    public function license()
    {
        return $this->belongsTo(License::class);
    }
}
